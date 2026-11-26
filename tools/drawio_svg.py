#!/usr/bin/env python3
"""drawio_svg: build editable draw.io diagrams as .drawio.svg files, using only the standard library.

A .drawio.svg file is a normal SVG picture (so it renders inside Markdown in the VS Code
preview and on GitHub) that also carries the draw.io diagram XML in its `content`
attribute (so draw.io desktop, app.diagrams.net and the VS Code "Draw.io Integration"
extension open it for editing, and re-render the picture when you save).

Use this only to CREATE a diagram. After that, edit the .drawio.svg in draw.io directly;
the per-topic generator scripts refuse to overwrite an existing file unless --force is given.
"""
from __future__ import annotations

import html
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import drawio_aws4

PALETTE = {  # name: (fill, stroke), the draw.io default colour set
    "blue": ("#dae8fc", "#6c8ebf"),
    "green": ("#d5e8d4", "#82b366"),
    "yellow": ("#fff2cc", "#d6b656"),
    "orange": ("#ffe6cc", "#d79b00"),
    "red": ("#f8cecc", "#b85450"),
    "purple": ("#e1d5e7", "#9673a6"),
    "gray": ("#f5f5f5", "#666666"),
    "white": ("#ffffff", "#666666"),
    "outline": ("none", "#666666"),
    "none": ("none", "none"),
    "aws-public": ("#F2F6E8", "#7AA116"),   # draw.io AWS public subnet fill
    "aws-private": ("#E6F6F7", "#00A4A6"),  # draw.io AWS private subnet fill
    "az": ("none", "#147EBA"),              # draw.io AWS availability zone (dashed, no fill)
    # AWS-style section colours (light fill + AWS category colour), for aws=True groups and cards
    "aws-appint": ("#FDF0F6", "#E7157B"), "aws-analytics": ("#F4EFFF", "#8C4FFF"),
    "aws-compute": ("#FEF3E8", "#ED7100"), "aws-storage": ("#F2F6E8", "#7AA116"),
    "aws-security": ("#FDEEF0", "#DD344C"), "aws-gen": ("#F5F6F7", "#7D8998"),
    "card": ("#FFFFFF", "#879196"), "exam": ("#FFF8E8", "#F2A93B"),
}
INK = "#1a1a1a"
LINE = "#555555"
FONT = "Helvetica, Arial, sans-serif"
CHAR_W = 0.56  # rough average glyph width, as a fraction of font size (fit warnings only)
LINE_H = 1.3   # line height, as a fraction of font size


# draw.io's own AWS library (mxgraph.aws4) by short icon name. No icon files are stored: in the draw.io model
# each icon is a native library shape, and the SVG preview draws the same draw.io stencil as vector paths
# (tools/drawio_aws4.py), so GitHub and draw.io show the same shape. Use only names listed here.
NETWORK, COMPUTE, STORAGE, DATABASE, MGMT, APPINT, GENERAL = (
    "#8C4FFF", "#ED7100", "#7AA116", "#C925D1", "#E7157B", "#E7157B", "#232F3E")
SECURITY, ANALYTICS = "#DD344C", "#8C4FFF"
DRAWIO_AWS = {  # icon file name: (kind, mxgraph.aws4 name, fill colour); kind "service" = resourceIcon tile
    "route53": ("service", "route_53", NETWORK), "cloudfront": ("service", "cloudfront", NETWORK),
    "global-accelerator": ("service", "global_accelerator", NETWORK), "elb": ("service", "elastic_load_balancing", NETWORK),
    "vpc": ("service", "vpc", NETWORK), "api-gateway": ("service", "api_gateway", APPINT),
    "appsync": ("service", "appsync", APPINT), "ec2": ("service", "ec2", COMPUTE), "lambda": ("service", "lambda", COMPUTE),
    "app-runner": ("service", "app_runner", COMPUTE), "beanstalk": ("service", "elastic_beanstalk", COMPUTE),
    "s3": ("service", "s3", STORAGE), "efs": ("service", "elastic_file_system", STORAGE),
    "ebs": ("service", "elastic_block_store", STORAGE), "rds": ("service", "rds", DATABASE),
    "aurora": ("service", "aurora", DATABASE), "elasticache": ("service", "elasticache", DATABASE),
    "opensearch": ("service", "elasticsearch_service", "#8C4FFF"), "cloudwatch": ("service", "cloudwatch_2", MGMT),
    "alb": ("resource", "application_load_balancer", NETWORK), "nlb": ("resource", "network_load_balancer", NETWORK),
    "gwlb": ("resource", "gateway_load_balancer", NETWORK), "clb": ("resource", "classic_load_balancer", NETWORK),
    "edge-location": ("resource", "edge_location", NETWORK), "eni": ("resource", "elastic_network_interface", NETWORK),
    "igw": ("resource", "internet_gateway", NETWORK), "nacl": ("resource", "network_access_control_list", NETWORK),
    "r53-hosted-zone": ("resource", "hosted_zone", NETWORK), "vpc-endpoints": ("resource", "endpoints", NETWORK),
    "ec2-ami": ("resource", "ami", COMPUTE), "ec2-eip": ("resource", "elastic_ip_address", COMPUTE),
    "ec2-instance": ("resource", "instance2", COMPUTE), "ec2-instances": ("resource", "instances", COMPUTE),
    "ec2-spot": ("resource", "spot_instance", COMPUTE), "ec2-autoscaling": ("resource", "auto_scaling2", COMPUTE),
    "lambda-fn": ("resource", "lambda_function", COMPUTE), "ebs-gp3": ("resource", "elastic_block_store_volume_gp3", STORAGE),
    "ebs-snapshot": ("resource", "snapshot", STORAGE), "ebs-volume": ("resource", "volume", STORAGE),
    "efs-fs": ("resource", "file_system", STORAGE), "efs-ia": ("resource", "elastic_file_system_infrequent_access", STORAGE),
    "efs-onezone": ("resource", "elastic_file_system_one_zone", STORAGE),
    "efs-standard": ("resource", "elastic_file_system_standard", STORAGE),
    "redis": ("resource", "elasticache_for_redis", DATABASE), "memcached": ("resource", "elasticache_for_memcached", DATABASE),
    "rds-multiaz": ("resource", "rds_multi_az", DATABASE), "rds-proxy": ("resource", "rds_proxy", DATABASE),
    "aurora-instance": ("resource", "aurora_instance", DATABASE), "cw-alarm": ("resource", "alarm", MGMT),
    "client": ("resource", "client", GENERAL), "users": ("resource", "users", GENERAL),
    "corp-dc": ("resource", "corporate_data_center", GENERAL), "internet": ("resource", "internet_alt1", GENERAL),
    "server": ("resource", "traditional_server", GENERAL),
    # S3 section (09-s3.md), checked against draw.io Sidebar-AWS4.js on 24 Nov 2026
    "s3-bucket": ("resource", "bucket", STORAGE), "s3-object": ("resource", "object", STORAGE),
    "s3-bucket-objects": ("resource", "bucket_with_objects", STORAGE), "s3-standard-ia": ("resource", "standard_ia", STORAGE),
    "s3-onezone-ia": ("resource", "one_zone_ia", STORAGE),
    "s3-glacier-ir": ("resource", "simple_storage_service_s3_glacier_instant_retrieval", STORAGE),
    "s3-glacier-fr": ("resource", "glacier", STORAGE), "s3-glacier-da": ("resource", "glacier_deep_archive", STORAGE),
    "s3-intelligent-tiering": ("resource", "intelligent_tiering", STORAGE), "s3-replication": ("resource", "replication", STORAGE),
    "s3-batch-ops": ("resource", "s3_batch_operations", STORAGE), "s3-storage-lens": ("resource", "s3_storage_lens", STORAGE),
    "s3-object-lock": ("resource", "s3_object_lock", STORAGE), "s3-mrap": ("resource", "s3_multi_region_access_points", STORAGE),
    "s3-access-points": ("resource", "general_access_points", STORAGE), "s3-vpc-access-points": ("resource", "vpc_access_points", STORAGE),
    "s3-object-lambda": ("resource", "s3_object_lambda", STORAGE),
    "s3-object-lambda-ap": ("resource", "s3_object_lambda_access_points", STORAGE), "glacier-vault": ("resource", "vault", STORAGE),
    "sns-topic": ("resource", "topic", APPINT), "sqs-queue": ("resource", "queue", APPINT),
    "iam-role": ("resource", "role", SECURITY), "iam-mfa": ("resource", "mfa_token", SECURITY),
    "iam-permissions": ("resource", "permissions", SECURITY), "kms-data-key": ("resource", "data_encryption_key", SECURITY),
    "encrypted-data": ("resource", "encrypted_data", SECURITY), "user": ("resource", "user", GENERAL),
    "kms": ("service", "key_management_service", SECURITY), "eventbridge": ("service", "eventbridge", APPINT),
    "athena": ("service", "athena", ANALYTICS), "cloudtrail": ("service", "cloudtrail", MGMT),
    "iam": ("service", "identity_and_access_management", SECURITY), "sns": ("service", "sns", APPINT),
    "sqs": ("service", "sqs", APPINT),
    # CloudFront + Global Accelerator section (10-cloudfront-global-accelerator.md), stencil names checked 24 Nov 2026
    "waf": ("service", "waf", SECURITY), "shield": ("service", "shield", SECURITY),
    "cloudfront-functions": ("resource", "cloudfront_functions", NETWORK), "globe": ("resource", "globe", GENERAL),
    "mobile-client": ("resource", "mobile_client", GENERAL), "iot-core": ("service", "iot_core", "#7AA116"),
    "gamelift": ("service", "gamelift", COMPUTE),
    # Storage extras section (11-storage-extras.md), stencil names checked against the aws4 set 25 Nov 2026
    "snowball": ("service", "snowball", STORAGE), "snowball-edge": ("service", "snowball_edge", STORAGE),
    "snowcone": ("service", "snowcone", STORAGE), "snowmobile": ("service", "snowmobile", STORAGE),
    "fsx": ("service", "fsx", STORAGE), "fsx-lustre": ("service", "fsx_for_lustre", STORAGE),
    "fsx-windows": ("service", "fsx_for_windows_file_server", STORAGE),
    "fsx-ontap": ("service", "fsx_for_netapp_ontap", STORAGE), "fsx-openzfs": ("service", "fsx_for_openzfs", STORAGE),
    "storage-gateway": ("service", "storage_gateway", STORAGE), "s3-file-gateway": ("resource", "s3_file_gateway", STORAGE),
    "fsx-file-gateway": ("resource", "fsx_file_gateway", STORAGE), "volume-gateway": ("resource", "volume_gateway", STORAGE),
    "tape-gateway": ("resource", "tape_gateway", STORAGE), "cached-volume": ("resource", "cached_volume", STORAGE),
    "stored-volume": ("resource", "non_cached_volume", STORAGE), "vtl": ("resource", "virtual_tape_library", STORAGE),
    "transfer-family": ("service", "transfer_family", "#7AA116"), "datasync": ("service", "datasync", "#7AA116"),
    "datasync-agent": ("resource", "agent", "#7AA116"), "data-transfer-terminal": ("resource", "data_transfer_terminal", "#7AA116"),
    "direct-connect": ("service", "direct_connect", NETWORK), "site-to-site-vpn": ("service", "site_to_site_vpn", NETWORK),
    "outposts": ("service", "outposts", COMPUTE), "hdfs": ("resource", "hdfs_cluster", ANALYTICS),
    "glacier-service": ("service", "glacier", STORAGE),
    # Integration & messaging section (12-integration-messaging.md), stencil names checked against the aws4 set 25 Nov 2026
    "kinesis-data-streams": ("service", "kinesis_data_streams", ANALYTICS),
    "firehose": ("service", "kinesis_data_firehose", ANALYTICS), "mq": ("service", "mq", APPINT),
    "mq-broker": ("resource", "mq_broker", APPINT), "sqs-message": ("resource", "message", APPINT),
    "email-notification": ("resource", "email_notification", APPINT),
    "http-notification": ("resource", "http_notification", APPINT), "redshift": ("service", "redshift", ANALYTICS),
    "flink": ("service", "managed_service_for_apache_flink", ANALYTICS),
    "msk": ("service", "managed_streaming_for_kafka", ANALYTICS), "dynamodb": ("service", "dynamodb", DATABASE),
    "generic-app": ("resource", "generic_application", GENERAL), "sensor": ("resource", "sensor", GENERAL),
    # EKS (stencil names checked against the aws4 set 26 Nov 2026)
    "eks": ("service", "eks", COMPUTE), "container": ("resource", "container_1", COMPUTE),
    "nat-gateway": ("resource", "nat_gateway", NETWORK),
}


# draw.io AWS *group* shapes (the containers in draw.io's AWS "Groups" panel: Region, VPC, subnets, ASG, ...).
# A group() whose icon is listed here becomes that container shape in the draw.io model (icon in its corner);
# a lone icon() of one of these becomes a borderless group shape, so only its corner icon shows.
DRAWIO_AWS_GROUP = {  # icon name: (draw.io group icon stencil, AWS colour from draw.io's sidebar)
    "aws-cloud": ("group_aws_cloud_alt", "#232F3E"), "region": ("group_region", "#00A4A6"), "vpc": ("group_vpc2", "#8C4FFF"),
    "asg-group": ("group_auto_scaling_group", "#D86613"), "spot-fleet": ("group_spot_fleet", "#D86613"),
    "private-subnet": ("group_security_group", "#00A4A6"), "public-subnet": ("group_security_group", "#7AA116"),
}
GROUP_ICON = 25  # draw.io draws a group's icon 25 x 25 at its top-left corner


def drawio_aws_style(name: str) -> str | None:
    """draw.io library style for a vendored icon, or None if it has no library match."""
    if name not in DRAWIO_AWS:
        return None
    kind, shape, fill = DRAWIO_AWS[name]
    common = ("sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;dashed=0;verticalLabelPosition=bottom;"
              "verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;")
    if kind == "service":
        return common + f"fillColor={fill};strokeColor=#ffffff;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.{shape};"
    return common + f"fillColor={fill};strokeColor=none;pointerEvents=1;shape=mxgraph.aws4.{shape};"


def icon_svg(name: str, x: float, y: float, w: float, h: float, defs: dict) -> str:
    """Vector SVG of an icon, drawn the way draw.io draws its library shape (symbols collected in defs)."""
    def use(shape, color, ux, uy, uw, uh):
        sid, symbol = drawio_aws4.stencil_symbol(shape, color)
        defs[sid] = symbol
        return f'<use xlink:href="#{sid}" x="{ux:g}" y="{uy:g}" width="{uw:g}" height="{uh:g}"/>'

    if name in DRAWIO_AWS_GROUP:
        shape, color = DRAWIO_AWS_GROUP[name]
        return use(shape, color, x, y, w, h)
    kind, shape, fill = DRAWIO_AWS[name]
    if kind == "service":  # mxgraph.aws4.resourceIcon: coloured tile, white stencil inset by 10%
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'
                + use(shape, "#ffffff", x + w * 0.1, y + h * 0.1, w * 0.8, h * 0.8))
    return use(shape, fill, x, y, w, h)


def _q(s: str) -> str:
    return html.escape(str(s), quote=True)


def _center(v: dict) -> tuple[float, float]:
    return v["x"] + v["w"] / 2, v["y"] + v["h"] / 2


def _perimeter(v: dict, tx: float, ty: float) -> tuple[float, float]:
    """Point where the ray from v's centre towards (tx, ty) leaves v's outline."""
    cx, cy = _center(v)
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    hw, hh = v["w"] / 2, v["h"] / 2
    if v["shape"] == "ellipse":
        s = 1 / math.sqrt((dx / hw) ** 2 + (dy / hh) ** 2)
    else:
        s = min(hw / abs(dx) if dx else math.inf, hh / abs(dy) if dy else math.inf)
    return cx + dx * s, cy + dy * s


def _midpoint(pts: list[tuple[float, float]]) -> tuple[float, float]:
    segs = [(a, b, math.dist(a, b)) for a, b in zip(pts, pts[1:])]
    half = sum(length for _, _, length in segs) / 2
    for a, b, length in segs:
        if length > 0 and half <= length:
            f = half / length
            return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        half -= length
    return pts[-1]


def _svg_text(lines, x, y, w, h, size, valign, align, bold, bold_first, italic, top_inset=0.0):
    lh = size * LINE_H
    n = len(lines)
    if valign == "top":
        first_c = y + 6 + lh / 2
    elif valign == "bottom":
        first_c = y + h - 6 - lh * (n - 0.5)
    else:
        first_c = y + top_inset + (h - top_inset - lh * n) / 2 + lh / 2
    ax, anchor = (x + 8, "start") if align == "left" else (x + w / 2, "middle")
    italic_attr = ' font-style="italic"' if italic else ""
    out = [f'<text font-family="{FONT}" font-size="{size}" fill="{INK}" text-anchor="{anchor}"{italic_attr}>']
    for i, line in enumerate(lines):
        weight = ' font-weight="bold"' if bold or (bold_first and i == 0 and n > 1) else ""
        out.append(f'<tspan x="{ax:.1f}" y="{first_c + i * lh + size * 0.35:.1f}"{weight}>'
                   f'{html.escape(line, quote=False)}</tspan>')
    out.append("</text>")
    return "".join(out)


class Diagram:
    def __init__(self, name: str, width: int, height: int, title: str | None = None):
        self.name, self.width, self.height = name, width, height
        self.vertices: list[dict] = []
        self.edges: list[dict] = []
        self.warnings: list[str] = []
        self._by_id: dict[str, dict] = {}
        if title:
            self.text("title", 0, 8, width, 28, title, size=16, bold=True)

    # ---- building ---------------------------------------------------------------
    def box(self, id, x, y, w, h, label, color="blue", *, shape="rect", size=12, bold=False,
            italic=False, dashed=False, valign="middle", align="center", bold_first=True,
            icon=None, icon_size=32):
        """icon = a DRAWIO_AWS / DRAWIO_AWS_GROUP name (draw.io aws4 library shape), drawn at the left of the box."""
        if id in self._by_id:
            raise ValueError(f"{self.name}: duplicate id {id!r}")
        pad = icon_size + 10 if icon else 0
        v = dict(id=id, x=x, y=y, w=w, h=h, lines=label.split("\n") if label else [], color=color,
                 shape=shape, size=size, bold=bold, italic=italic, dashed=dashed, valign=valign,
                 align=align, bold_first=bold_first, pad_left=pad, image=None)
        self.vertices.append(v)
        self._by_id[id] = v
        self._check_fit(v)
        if icon:
            iy = y + 6 if valign == "top" else y + (h - icon_size) / 2
            self.icon(f"{id}-icon", x + 8, iy, icon, icon_size)
        return id

    def group(self, id, x, y, w, h, label, color="gray", *, dashed=False, size=13,
              valign="top", align="center", icon=None, icon_size=24, aws=False):
        """A labelled region. Add it BEFORE the boxes inside it, so it is drawn behind them.

        aws=True draws it like a draw.io AWS group: square corners, label top-left, and the icon (if any) as a
        25 px tile in the top-left corner (like the Region / VPC groups)."""
        if aws and icon not in DRAWIO_AWS_GROUP:
            gid = self.box(id, x, y, w, h, label, color, size=size, bold=True, dashed=dashed,
                           valign="top", align="left", icon=icon, icon_size=GROUP_ICON)
            v = self._by_id[gid]
            v["square"] = True
            v["pad_left"] = GROUP_ICON + 4 if icon else 2
            if icon:
                self._by_id[f"{gid}-icon"].update(x=x, y=y)
            return gid
        gid = self.box(id, x, y, w, h, label, color, size=size, bold=True, dashed=dashed,
                       valign=valign, align=align, icon=icon, icon_size=icon_size)
        if icon in DRAWIO_AWS_GROUP:  # draw.io: its AWS container shape draws the icon itself, top-left, 25 px
            v, ic = self._by_id[gid], self._by_id[f"{gid}-icon"]
            v["drawio_group"], v["aws_stroke"] = DRAWIO_AWS_GROUP[icon]
            ic["svg_only"] = True
            ic.update(x=x, y=y, w=GROUP_ICON, h=GROUP_ICON)
        return gid

    def icon(self, id, x, y, name, size=40):
        """An AWS icon on its own: a native draw.io AWS library shape (vector paths in the SVG preview)."""
        if name not in DRAWIO_AWS and name not in DRAWIO_AWS_GROUP:
            raise KeyError(f"{self.name}: {name!r} is not in DRAWIO_AWS / DRAWIO_AWS_GROUP (draw.io aws4 library)")
        v = self._by_id.get(self.box(id, x, y, size, size, "", "none"))
        style = drawio_aws_style(name)
        if style is None:  # group icon on its own: borderless group shape, so only its corner icon shows
            shape, color = DRAWIO_AWS_GROUP[name]
            style = ("sketch=0;outlineConnect=0;html=1;dashed=0;fillColor=none;grStroke=0;"
                     f"strokeColor={color};grIconSize={size};shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.{shape};")
        v["shape"], v["icon"], v["drawio_style"] = "image", name, style
        return id

    def text(self, id, x, y, w, h, label, *, size=12, bold=False, italic=False, align="center", valign="middle"):
        return self.box(id, x, y, w, h, label, "none", shape="text", size=size, bold=bold,
                        italic=italic, align=align, bold_first=False, valign=valign)

    def edge(self, src, tgt, label=None, *, dashed=False, both=False, points=None, size=10):
        for end in (src, tgt):
            if end not in self._by_id:
                raise KeyError(f"{self.name}: edge end {end!r} is not a vertex")
        self.edges.append(dict(id=f"e{len(self.edges)}", src=src, tgt=tgt,
                               lines=label.split("\n") if label else [], dashed=dashed,
                               both=both, points=list(points or []), size=size))

    def _check_fit(self, v):
        pad = (0 if v["shape"] == "text" else 12) + v.get("pad_left", 0)
        for i, line in enumerate(v["lines"]):
            bold = v["bold"] or (v["bold_first"] and i == 0 and len(v["lines"]) > 1)
            est = len(line) * v["size"] * CHAR_W * (1.08 if bold else 1.0)
            if est > v["w"] - pad:
                self.warnings.append(f"{self.name}/{v['id']}: {line!r} needs ~{est:.0f}px, has {v['w'] - pad}px")
        if v["valign"] == "middle":
            need = len(v["lines"]) * v["size"] * LINE_H + (0 if v["shape"] == "text" else 6)
            need += 16 if v["shape"] == "cylinder" else 0
            if need > v["h"]:
                self.warnings.append(f"{self.name}/{v['id']}: {len(v['lines'])} lines need ~{need:.0f}px, has {v['h']}px")

    # ---- SVG rendering ------------------------------------------------------------
    def _route(self, e) -> list[tuple[float, float]]:
        s, t = self._by_id[e["src"]], self._by_id[e["tgt"]]
        first = e["points"][0] if e["points"] else _center(t)
        last = e["points"][-1] if e["points"] else _center(s)
        return [_perimeter(s, *first), *e["points"], _perimeter(t, *last)]

    @staticmethod
    def _svg_vertex(v, defs: dict) -> str:
        fill, stroke = PALETTE[v["color"]]
        x, y, w, h = v["x"], v["y"], v["w"], v["h"]
        dash = ' stroke-dasharray="6 4"' if v["dashed"] else ""
        paint = f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}'
        out, inset = [], 0.0
        if v["shape"] == "image":
            return icon_svg(v["icon"], x, y, w, h, defs)
        if v.get("drawio_group") or v.get("square"):  # AWS container: square corners, AWS colour border
            stroke = v.get("aws_stroke", stroke)
            paint = f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}'
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" {paint}/>')
        elif v["shape"] == "rect":
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" ry="8" {paint}/>')
        elif v["shape"] == "ellipse":
            out.append(f'<ellipse cx="{x + w / 2}" cy="{y + h / 2}" rx="{w / 2}" ry="{h / 2}" {paint}/>')
        elif v["shape"] == "cylinder":
            r, ry = w / 2, 8
            out.append(f'<path d="M{x},{y + ry} L{x},{y + h - ry} A{r},{ry} 0 0 0 {x + w},{y + h - ry} '
                       f'L{x + w},{y + ry}" {paint}/>')
            out.append(f'<ellipse cx="{x + r}" cy="{y + ry}" rx="{r}" ry="{ry}" {paint}/>')
            inset = 2 * ry
        pad = v.get("pad_left", 0)
        out.append(_svg_text(v["lines"], x + pad, y, w - pad, h, v["size"], v["valign"], v["align"], v["bold"],
                             v["bold_first"], v["italic"], top_inset=inset))
        return "".join(out)

    @staticmethod
    def _svg_edge(e, pts) -> str:
        d = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts)
        dash = ' stroke-dasharray="6 4"' if e["dashed"] else ""
        start = ' marker-start="url(#arrow)"' if e["both"] else ""
        return (f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.5"{dash}{start} '
                f'marker-end="url(#arrow)"/>')

    @staticmethod
    def _svg_edge_label(e, pts) -> str:
        if not e["lines"]:
            return ""
        mx, my = _midpoint(pts)
        size = e["size"]
        w = max(len(line) for line in e["lines"]) * size * CHAR_W + 8
        h = size * LINE_H * len(e["lines"]) + 4
        x, y = mx - w / 2, my - h / 2
        return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#ffffff"/>'
                + _svg_text(e["lines"], x, y, w, h, size, "middle", "center", False, False, False))

    # ---- draw.io XML ----------------------------------------------------------------
    @staticmethod
    def _mx_value(lines, bold_first, italic) -> str:
        parts = [html.escape(line, quote=False) for line in lines]
        if bold_first and len(parts) > 1:
            parts[0] = f"<b>{parts[0]}</b>"
        value = "<br>".join(parts)
        return f"<i>{value}</i>" if italic else value

    @staticmethod
    def _mx_vertex_style(v) -> str:
        fill, stroke = PALETTE[v["color"]]
        if v.get("drawio_group"):  # draw.io AWS container: icon top-left, label beside it
            fill, stroke = PALETTE[v["color"]]
            style = (f"sketch=0;outlineConnect=0;html=1;whiteSpace=wrap;shape=mxgraph.aws4.group;"
                     f"grIcon=mxgraph.aws4.{v['drawio_group']};grStroke=1;fillColor={fill};strokeColor={v['aws_stroke']};"
                     f"strokeWidth=1.5;fontSize={v['size']};fontColor={INK};fontStyle=1;fontFamily=Helvetica;"
                     f"align={v['align']};verticalAlign=top;spacingLeft=30;spacingTop=4;")
            return style + ("dashed=1;dashPattern=6 4;" if v["dashed"] else "dashed=0;")
        if v["shape"] == "image" and v.get("drawio_style"):
            return v["drawio_style"]  # native draw.io AWS library shape (SVG preview keeps the icon file)
        common = (f"whiteSpace=wrap;html=1;fontSize={v['size']};fontColor={INK};fontFamily=Helvetica;"
                  f"align={v['align']};verticalAlign={v['valign']};")
        if v["shape"] == "text":
            style = "text;strokeColor=none;fillColor=none;" + common
        else:
            shape = {"rect": "rounded=0;" if v.get("square") else "rounded=1;absoluteArcSize=1;arcSize=16;",
                     "ellipse": "ellipse;",
                     "cylinder": "shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=8;"}[v["shape"]]
            style = shape + f"fillColor={fill};strokeColor={stroke};strokeWidth=1.5;" + common
        if v["dashed"]:
            style += "dashed=1;dashPattern=6 4;"
        if v["bold"]:
            style += "fontStyle=1;"
        if v["align"] == "left" or v.get("pad_left"):
            style += f"spacingLeft={v.get('pad_left', 0) + (6 if v['align'] == 'left' else 0)};"
        if v["valign"] in ("top", "bottom"):
            style += "spacingTop=2;spacingBottom=2;"
        return style

    @staticmethod
    def _mx_edge_style(e) -> str:
        style = (f"html=1;rounded=0;endArrow=classic;endFill=1;strokeColor={LINE};strokeWidth=1.5;"
                 f"fontSize={e['size']};fontColor={INK};labelBackgroundColor=#ffffff;")
        style += "startArrow=classic;startFill=1;" if e["both"] else "startArrow=none;"
        if e["dashed"]:
            style += "dashed=1;dashPattern=6 4;"
        return style

    def to_mxfile(self) -> str:
        cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
        for v in self.vertices:
            if v.get("svg_only"):
                continue
            value = self._mx_value(v["lines"], v["bold_first"] and not v["bold"], v["italic"])
            cells.append(f'<mxCell id="v-{_q(v["id"])}" value="{_q(value)}" style="{_q(self._mx_vertex_style(v))}" '
                         f'vertex="1" parent="1"><mxGeometry x="{v["x"]}" y="{v["y"]}" width="{v["w"]}" '
                         f'height="{v["h"]}" as="geometry"/></mxCell>')
        for e in self.edges:
            pts = "".join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in e["points"])
            geometry = (f'<mxGeometry relative="1" as="geometry"><Array as="points">{pts}</Array></mxGeometry>'
                        if pts else '<mxGeometry relative="1" as="geometry"/>')
            value = self._mx_value(e["lines"], False, False)
            cells.append(f'<mxCell id="{e["id"]}" value="{_q(value)}" style="{_q(self._mx_edge_style(e))}" '
                         f'edge="1" parent="1" source="v-{_q(e["src"])}" target="v-{_q(e["tgt"])}">'
                         f'{geometry}</mxCell>')
        model = (f'<mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" '
                 f'arrows="1" fold="1" page="1" pageScale="1" pageWidth="{self.width}" '
                 f'pageHeight="{self.height}" math="0" shadow="0"><root>{"".join(cells)}</root></mxGraphModel>')
        return (f'<mxfile host="drawio_svg.py" agent="drawio_svg.py" version="24.7.17" type="device">'
                f'<diagram id="{_q(self.name)}" name="{_q(self.name)}">{model}</diagram></mxfile>')

    def to_svg(self) -> str:
        routes = [(e, self._route(e)) for e in self.edges]
        defs: dict[str, str] = {}
        body = ("".join(self._svg_vertex(v, defs) for v in self.vertices)
                + "".join(self._svg_edge(e, pts) for e, pts in routes)
                + "".join(self._svg_edge_label(e, pts) for e, pts in routes))
        w, h = self.width, self.height
        xlink = ' xmlns:xlink="http://www.w3.org/1999/xlink"' if defs else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg"{xlink} version="1.1" width="{w}" height="{h}" '
                f'viewBox="0 0 {w} {h}" content="{_q(self.to_mxfile())}">'
                f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
                f'markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/>'
                f'</marker>{"".join(defs.values())}</defs><rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>{body}</svg>')

    # ---- output ---------------------------------------------------------------------
    def save(self, out_dir: Path, force: bool = False) -> Path | None:
        out = Path(out_dir) / f"{self.name}.drawio.svg"
        if out.exists() and not force:
            return None  # never overwrite a diagram that may have been edited in draw.io
        svg = self.to_svg()
        root = ET.fromstring(svg)               # the SVG must be well-formed
        model = ET.fromstring(root.get("content"))  # and so must the embedded draw.io XML
        assert model.find("./diagram/mxGraphModel/root") is not None, "draw.io model missing"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg, encoding="utf-8")
        return out
