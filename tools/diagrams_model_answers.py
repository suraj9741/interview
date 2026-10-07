#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/hemant-model-answers.md.

Run once:  python3 tools/diagrams_model_answers.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "diagrams"


def observability_stack():
    d = Diagram("46-observability-stack", 1000, 600,
                "Observability stack: metrics, logs and traces (open source, budget-friendly)")
    d.text("h-src", 20, 46, 180, 22, "Sources", size=13, bold=True)
    d.text("h-col", 280, 46, 190, 22, "Collectors", size=13, bold=True)
    d.text("h-be", 545, 46, 200, 22, "Store and query", size=13, bold=True)
    d.text("h-s3", 810, 46, 180, 22, "Long-term storage", size=13, bold=True)

    d.box("src-m", 20, 80, 180, 54, "Apps & nodes\nexpose /metrics", "blue")
    d.box("src-l", 20, 165, 180, 54, "Pod stdout / stderr\nlogs", "blue")
    d.box("src-t", 20, 250, 180, 54, "Apps with\nOpenTelemetry SDK", "blue")
    d.box("onprem", 20, 335, 180, 54, "On-prem servers\nAlloy / OTel agents", "purple")

    d.box("prom", 280, 80, 190, 54, "Prometheus\n(scrapes, alert rules)", "orange")
    d.box("fb", 280, 165, 190, 54, "Fluent Bit / Alloy\n(DaemonSet on each node)", "orange")
    d.box("otel", 280, 250, 190, 54, "OTel Collector\n(receives and samples)", "orange")

    d.group("be", 545, 66, 200, 252, "", "outline", dashed=True)
    d.box("mimir", 560, 80, 170, 54, "Mimir / Thanos\n(long-term metrics)", "green")
    d.box("loki", 560, 165, 170, 54, "Loki\n(indexes labels only)", "green")
    d.box("tempo", 560, 250, 170, 54, "Tempo\n(traces)", "green")

    d.box("s3", 820, 80, 160, 224, "Amazon S3\ncheap, durable\nobject storage", "yellow", shape="cylinder")

    d.box("grafana", 300, 410, 445, 64,
          "Grafana\ndashboards for metrics, logs and traces,\nlinked by labels and trace IDs", "blue")
    d.box("alert", 300, 505, 210, 54, "Alerting\nAlertmanager / Grafana", "red")
    d.box("notify", 600, 505, 190, 54, "On-call\nSlack · PagerDuty · email", "white")

    d.edge("src-m", "prom", "scraped\n(pull)")
    d.edge("src-l", "fb", "tailed")
    d.edge("src-t", "otel", "OTLP")
    d.edge("prom", "mimir", "remote_write")
    d.edge("fb", "loki", "push")
    d.edge("otel", "tempo", "OTLP")
    d.edge("mimir", "s3")
    d.edge("loki", "s3")
    d.edge("tempo", "s3")
    d.edge("onprem", "be", "push over VPN / Direct Connect", points=[(645, 362)])
    d.edge("grafana", "be", "queries: PromQL · LogQL · TraceQL", points=[(705, 390)])
    d.edge("grafana", "alert", "alert rules")
    d.edge("alert", "notify", "notify")
    d.text("caption", 0, 568, 1000, 26,
           "Alert on the golden signals; logs and traces explain why. All long-term data sits in cheap S3 storage.",
           size=11)
    return d


ALL = [observability_stack]

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
