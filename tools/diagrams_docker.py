#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/docker/*.md.

Run once:  python3 tools/diagrams_docker.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "docker" / "diagrams"


def container_vs_vm():
    d = Diagram("01-container-vs-vm", 780, 400, "Virtual machines vs containers")
    d.text("vm-h", 20, 44, 340, 24, "Virtual machines", size=14, bold=True)
    d.text("ct-h", 420, 44, 340, 24, "Containers", size=14, bold=True)
    for i, x in enumerate((25, 140, 255)):
        d.box(f"vm-app{i}", x, 75, 105, 30, "App", "blue")
        d.box(f"vm-lib{i}", x, 110, 105, 30, "Bins / Libs", "yellow")
        d.box(f"vm-os{i}", x, 145, 105, 38, "Guest OS", "orange")
    d.box("hyper", 25, 192, 335, 32, "Hypervisor", "purple")
    d.box("vm-host", 25, 230, 335, 32, "Host operating system", "gray")
    d.box("vm-hw", 25, 268, 335, 32, "Hardware", "white")
    for i, x in enumerate((425, 540, 655)):
        d.box(f"ct-app{i}", x, 110, 105, 30, "App", "blue")
        d.box(f"ct-lib{i}", x, 145, 105, 38, "Bins / Libs", "yellow")
    d.box("engine", 425, 192, 335, 32, "Container runtime (Docker Engine)", "green")
    d.box("ct-host", 425, 230, 335, 32, "Host OS kernel (shared by all containers)", "gray")
    d.box("ct-hw", 425, 268, 335, 32, "Hardware", "white")
    d.text("vm-note", 20, 310, 340, 40,
           "Each VM runs its own guest OS kernel\nGBs · boots in tens of seconds · strong isolation", size=11)
    d.text("ct-note", 420, 310, 340, 40,
           "Containers share the host kernel\nMBs · start in milliseconds · lighter isolation", size=11)
    d.text("bottom", 0, 360, 780, 28,
           "A VM virtualises the hardware · a container virtualises the operating system", size=13, bold=True)
    return d


def architecture():
    d = Diagram("02-docker-architecture", 820, 495, "Docker architecture: from docker run to a running process")
    d.box("cli", 30, 60, 160, 54, "docker CLI\n(the client)", "blue")
    d.box("dockerd", 320, 60, 180, 54, "dockerd\n(Docker daemon)", "blue")
    d.box("registry", 620, 60, 180, 54, "Registry\n(Docker Hub · ECR)", "gray")
    d.box("containerd", 320, 165, 180, 54, "containerd\n(manages containers)", "green")
    d.box("runc", 620, 165, 180, 54, "runc\n(creates it, then exits)", "yellow")
    d.box("shim", 320, 270, 180, 54, "containerd-shim\n(stays as the parent)", "green")
    d.box("app", 620, 270, 180, 54, "Your app\n(PID 1 in the container)", "orange")
    d.group("kernel", 30, 375, 770, 100, "Linux kernel", "gray")
    d.box("ns", 60, 410, 220, 50, "namespaces\n(what it can SEE)", "purple")
    d.box("cg", 305, 410, 220, 50, "cgroups\n(what it can USE)", "purple")
    d.box("ofs", 550, 410, 220, 50, "overlayfs\n(layered root filesystem)", "purple")
    d.edge("cli", "dockerd", "REST API over\n/var/run/docker.sock")
    d.edge("dockerd", "registry", "pull image", dashed=True)
    d.edge("dockerd", "containerd", "gRPC")
    d.edge("containerd", "shim", "starts")
    d.edge("shim", "runc", "calls")
    d.edge("runc", "app", "starts the process")
    d.edge("shim", "app", "parent: holds stdio\nand exit code", dashed=True)
    d.edge("app", "kernel", "runs on the kernel, isolated and limited by", points=[(710, 350), (415, 350)])
    return d


def overlay():
    d = Diagram("02-overlay2-layers", 740, 350, "How a container's filesystem is built (overlay2)")
    d.box("merged", 40, 55, 420, 40, "merged view: what the container sees as /", "green")
    d.box("upper", 40, 115, 420, 46, "upperdir: the container's writable layer\n(thrown away on docker rm)", "orange")
    d.group("lower", 30, 172, 440, 122, "", "outline", dashed=True)
    d.box("l3", 40, 180, 420, 32, "Layer 3: COPY . /app", "blue")
    d.box("l2", 40, 217, 420, 32, "Layer 2: RUN pip install -r requirements.txt", "blue")
    d.box("l1", 40, 254, 420, 32, "Layer 1: base image (python:3.12-slim)", "blue")
    d.text("upper-note", 480, 113, 240, 50,
           "Copy-on-write: an image file is\ncopied up here before it changes", size=11, align="left")
    d.text("lower-note", 480, 192, 240, 80,
           "lowerdir = the image layers:\nread-only and shared by every\ncontainer started from this image",
           size=11, align="left")
    d.edge("upper", "merged")
    d.text("caption", 0, 298, 740, 42,
           "Image layers never change, so many containers can share them.\n"
           "Data written to the writable layer is lost on docker rm, so keep it in volumes.", size=12)
    return d


def lifecycle():
    d = Diagram("04-container-lifecycle", 800, 330, "Container lifecycle")
    d.text("run-note", 20, 42, 320, 22, "docker run = docker create + docker start", size=11, italic=True, align="left")
    d.box("image", 20, 110, 110, 50, "Image", "gray")
    d.box("created", 210, 110, 110, 50, "Created", "blue")
    d.box("running", 420, 110, 110, 50, "Running", "green")
    d.box("exited", 650, 110, 110, 50, "Exited\n(stopped)", "orange")
    d.box("paused", 420, 240, 110, 44, "Paused", "purple")
    d.box("removed", 650, 240, 110, 44, "Removed", "red")
    d.edge("image", "created", "docker\ncreate")
    d.edge("created", "running", "docker start")
    d.edge("running", "exited", "docker stop\nor app exits")
    d.edge("running", "paused", "docker pause /\nunpause", both=True)
    d.edge("exited", "removed", "docker rm")
    d.edge("exited", "running", "docker start (again)", points=[(705, 75), (475, 75)])
    d.text("caption", 0, 296, 800, 26,
           "docker stop = SIGTERM, then SIGKILL after 10 s · exit code 137 = killed (often out of memory)", size=12)
    return d


def multistage():
    d = Diagram("06-multi-stage-build", 780, 280, "Multi-stage build: only the final stage ships")
    d.group("s1", 20, 50, 330, 180, "Stage 1: build (FROM golang:1.23 AS build)", "gray", size=12)
    d.box("tools", 40, 92, 290, 52, "Compiler, SDK, source code,\ndependency cache", "orange")
    d.box("bin1", 40, 160, 290, 48, "go build → /app (one binary)", "blue")
    d.group("s2", 430, 50, 330, 180, "Stage 2: runtime (FROM distroless)", "green", size=12)
    d.box("note2", 450, 92, 290, 52,
          "No compiler · no shell · no package manager\n→ small image, few vulnerabilities", "white",
          size=11, bold_first=False)
    d.box("bin2", 450, 160, 290, 48, "/app (the binary only)", "blue")
    d.edge("bin1", "bin2", "COPY --from=build\n/app /app")
    d.text("caption", 0, 242, 780, 28,
           "The build tools stay behind in stage 1, so the final image is often 10–20 MB instead of ~1 GB.", size=12)
    return d


def mounts():
    d = Diagram("07-mount-types", 760, 350, "Three ways to give a container storage")
    d.group("ct", 20, 50, 240, 250, "Container", "blue")
    d.box("p1", 40, 95, 200, 44, "/var/lib/postgresql/data", "white", size=11)
    d.box("p2", 40, 170, 200, 44, "/app/src", "white", size=11)
    d.box("p3", 40, 245, 200, 44, "/app/cache", "white", size=11)
    d.group("host", 400, 50, 340, 250, "Docker host", "gray")
    d.box("vol", 420, 90, 300, 54, "Volume (managed by Docker)\n/var/lib/docker/volumes/db-data/_data", "green", size=11)
    d.box("bind", 420, 165, 300, 54, "Bind mount (any host path)\n/Users/me/project/src", "yellow", size=11)
    d.box("tmp", 420, 240, 300, 54, "tmpfs (memory only)\nin RAM, never written to disk", "purple", size=11)
    d.edge("p1", "vol", "volume")
    d.edge("p2", "bind", "bind mount")
    d.edge("p3", "tmp", "tmpfs")
    d.text("caption", 0, 310, 760, 30,
           "Volume = production data · Bind mount = local development and config · tmpfs = secrets and temp files",
           size=12)
    return d


def bridge():
    d = Diagram("08-bridge-network", 820, 500, "How the default bridge network works")
    d.box("inet", 315, 42, 190, 40, "Internet / your browser", "gray", shape="ellipse")
    d.group("host", 20, 100, 780, 380, "Docker host (Linux)", "gray", align="left")
    d.box("eth0", 320, 140, 180, 46, "eth0 (host network card)\nhost IP, e.g. 10.0.1.25", "blue", size=11)
    d.box("ipt", 560, 140, 220, 46, "iptables NAT rules\n-p → DNAT · outbound → MASQUERADE", "red", size=11)
    d.box("docker0", 270, 225, 280, 46, "docker0 bridge (virtual switch)\n172.17.0.1/16", "green")
    d.group("ca", 50, 305, 300, 120, "Container A (own network namespace)", "yellow", dashed=True, size=12,
            valign="bottom")
    d.box("etha", 80, 330, 240, 48, "eth0 · 172.17.0.2\nnginx listening on :80", "white", size=11)
    d.group("cb", 470, 305, 300, 120, "Container B (own network namespace)", "yellow", dashed=True, size=12,
            valign="bottom")
    d.box("ethb", 500, 330, 240, 48, "eth0 · 172.17.0.3\napi listening on :8000", "white", size=11)
    d.text("note", 40, 436, 740, 36,
           "Containers on the default bridge reach each other by IP only.\n"
           "Name lookup (Docker DNS at 127.0.0.11) works only on user-defined networks.", size=11)
    d.edge("inet", "eth0", "request to host:8080", both=True)
    d.edge("eth0", "ipt", dashed=True, both=True)
    d.edge("eth0", "docker0", "NAT / routing", both=True)
    d.edge("docker0", "etha", "veth pair", both=True)
    d.edge("docker0", "ethb", "veth pair", both=True)
    return d


def packet_flow():
    d = Diagram("08-packet-flow", 1000, 740, "A packet's journey: going out (MASQUERADE) and coming in (DNAT)")
    out_x, in_x, w, h = 255, 520, 235, 52
    d.box("h-out", out_x, 44, w, 44, "OUTBOUND ↓\ncontainer → internet", "none", shape="text", size=13)
    d.box("h-in", in_x, 44, w, 44, "INBOUND ↑  (-p 8080:80)\ninternet → container", "none", shape="text", size=13)
    rows = [  # (colour, outbound label, inbound label); the same pieces, walked in opposite directions
        ("yellow", "Container eth0 · 172.17.0.2\nthe app sends a packet",
                   "Container eth0 · 172.17.0.2 : 80\nnginx receives the request"),
        ("orange", "veth pair (the door)\ncontainer side → host side",
                   "veth pair (the door)\nhost side → container side"),
        ("green", "docker0 bridge · 172.17.0.1\nthe container's default gateway",
                  "docker0 bridge\nthe corridor to the container"),
        ("gray", "Host routing\nnot for me, so send it out of eth0",
                 "Host routing\n172.17.0.2 lives on docker0"),
        ("red", "iptables MASQUERADE\nin POSTROUTING: change FROM",
                "iptables DNAT\nin PREROUTING: change TO"),
        ("blue", "Host eth0 · 10.0.1.25\nthe packet leaves the computer",
                 "Host eth0 · 10.0.1.25 : 8080\nthe request arrives"),
        ("gray", "Internet\ngoogle.com · 142.250.x.x",
                 "Internet\nyour browser · 49.36.x.x"),
    ]
    for i, (color, out_label, in_label) in enumerate(rows):
        y = 100 + i * 82
        shape = "ellipse" if i == len(rows) - 1 else "rect"
        d.box(f"o{i}", out_x, y, w, h, out_label, color, shape=shape, size=11)
        d.box(f"i{i}", in_x, y, w, h, in_label, color, shape=shape, size=11)
    for i in range(len(rows) - 1):
        d.edge(f"o{i}", f"o{i + 1}")
        d.edge(f"i{i + 1}", f"i{i}")
    d.box("n-out-before", 20, 170, 220, 130,
          "Before MASQUERADE\nFROM 172.17.0.2 : 45000\nTO 142.250.x.x : 443\n\nStill the private IP:\nthe internet can't reply to it",
          "purple", size=11, align="left")
    d.box("n-out-after", 20, 480, 220, 130,
          "After MASQUERADE\nFROM 10.0.1.25 : 45000\nTO 142.250.x.x : 443\n\nIt wears the host's address,\nso the reply comes back here",
          "purple", size=11, align="left")
    d.box("n-in-after", 775, 170, 205, 130,
          "After DNAT\nFROM 49.36.x.x : 51000\nTO 172.17.0.2 : 80\n\nNow routing sends it to\ndocker0, not to the host",
          "purple", size=11, align="left")
    d.box("n-in-before", 775, 480, 205, 130,
          "Arrives as\nFROM 49.36.x.x : 51000\nTO 10.0.1.25 : 8080\n\nThe browser only knows\nthe host's address",
          "purple", size=11, align="left")
    d.text("footer", 20, 664, 960, 60,
           "Red row = the only place an address changes. MASQUERADE changes FROM (going out); DNAT changes TO (coming in).\n"
           "Replies travel the same path backwards: conntrack remembers each change and reverses it automatically.\n"
           "Only the first packet of a connection hits the NAT rule; conntrack handles the rest.", size=11)
    return d


def compose():
    d = Diagram("09-compose", 900, 345, "Docker Compose: one network, services found by name")
    d.box("browser", 20, 140, 150, 54, "Browser / curl\nlocalhost:8000", "gray")
    d.group("net", 220, 50, 500, 260, "Compose project network (DNS by service name)", "blue", dashed=True)
    d.box("api", 250, 140, 150, 54, "api\n(build: .)", "blue")
    d.text("dep", 240, 200, 170, 40, "depends_on: db\n(condition: service_healthy)", size=10, italic=True)
    d.box("db", 530, 85, 170, 54, "db\npostgres:16 + healthcheck", "green", size=11)
    d.box("cache", 530, 215, 170, 54, "cache\nredis:7", "orange")
    d.box("vol", 760, 80, 120, 64, "db-data\n(volume)", "purple", shape="cylinder")
    d.edge("browser", "api", "ports\n8000:8000")
    d.edge("api", "db", "db:5432")
    d.edge("api", "cache", "cache:6379")
    d.edge("db", "vol", "mount", dashed=True)
    d.text("caption", 0, 316, 900, 24,
           "docker compose up -d starts everything. api reaches Postgres at db:5432, with no -p needed between services.",
           size=11)
    return d


ALL = [container_vs_vm, architecture, overlay, lifecycle, multistage, mounts, bridge, packet_flow, compose]

if __name__ == "__main__":
    force = "--force" in sys.argv
    warnings = []
    for build in ALL:
        diagram = build()
        warnings += diagram.warnings
        path = diagram.save(OUT, force=force)
        print(f"{'wrote  ' if path else 'skipped'} {diagram.name}.drawio.svg"
              f"{'' if path else '  (exists; use --force to overwrite)'}")
    for w in warnings:
        print("WARN", w)
