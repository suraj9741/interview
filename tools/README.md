# Diagram tools

Every diagram in `interview-prep/` is an editable `.drawio.svg` file. GitHub shows it as a picture, and draw.io (desktop, app.diagrams.net or the VS Code extension) opens it for editing. The files are made with Python and the standard library only:

| File | What it does |
|---|---|
| `drawio_svg.py` | The `Diagram` API (`box`, `group`, `text`, `icon`, `edge`). It writes the draw.io model and the SVG preview. |
| `drawio_aws4.py` | Loads draw.io's own stencil sets (AWS `aws4`, `kubernetes`) from a pinned npm package. It caches them in `~/.cache/drawio-aws4/` and draws them as vector paths in the SVG preview. No icon files are stored in this repo. |
| `diagrams_<topic>.py` | One generator per topic folder. Run `python3 tools/diagrams_<topic>.py` to create missing diagrams. Existing files are skipped, because they may have been edited in draw.io. |
| `restyle_drawio.py` | Redraws existing diagrams in the current style. It does not change the content: every label, position and arrow is kept. |

## Diagram style rules

Since 26 Nov 2026 all diagrams use the AWS architecture look of `aws/diagrams/eks-01-worker-nodes.drawio.svg`. `drawio_svg.THEME = "aws"` applies it automatically.

1. **Containers look like draw.io AWS groups.** They have square corners and the label at the top left. When the label names something with an icon, the group gets a 25 px corner icon:
   - AWS groups: `aws-cloud`, `region`, `vpc`, `public-subnet`, `private-subnet` and `asg-group` use draw.io's own AWS group shapes.
   - Kubernetes groups: node, control plane and pod get the Kubernetes icon.
2. **Real icons, not plain boxes.** Use draw.io library shapes only:
   - AWS `mxgraph.aws4.*` for AWS services and for general things (client, users, internet, server, router, firewall, database, container, git, CLI, logs).
   - Kubernetes `mxgraph.kubernetes.icon` for pod, node, svc, deploy, rs, sts, ds, ing, hpa, cm, secret, pvc, api, etcd, sched, kubelet, k-proxy and so on.
   - The names are in `DRAWIO_AWS`, `DRAWIO_AWS_GROUP` and `DRAWIO_K8S`. Never add icon files to the repo.
3. **In hand-drawn diagrams, put the icon above its label.** Use the `node()` helper in `diagrams_aws.py`: the icon with its label centred below it, as in the EKS diagram. For lists, use `row()` (icon on the left, label beside it, no border).
4. **Boxes get icons automatically.** When the first line of a box names a service or tool, and the text still fits, `box()` adds the matching icon at the left (`ICON_RULES`). The keyword must come near the start of the line (a name, not a sentence). `ICON_EXCLUDE` lists labels that only mention a keyword. Pass `auto_icon=False` to turn this off for one box.
5. **Colours: the names keep their meaning.** They are shown as a light fill with an AWS category border:
   - green = right or good, red = wrong or bad, yellow = exam tip or warning, blue = neutral flow, orange = compute or important, purple = analytics, gray = background.
   - Section palettes: `aws-appint`, `aws-analytics`, `aws-compute`, `aws-storage`, `aws-security` and `aws-gen`. Use `card` for a plain white panel and `exam` for exam boxes.
6. **Tables have square cells.** Use `square()`.
7. **Content rules still apply:**
   - The diagram comes first in each note.
   - Never drop a fact to make a diagram fit. Make the diagram bigger instead.
   - Each folder uses only diagrams from its own `diagrams/` folder. Copy a diagram in rather than pointing at another folder.

## Restyling existing diagrams

```bash
python3 tools/restyle_drawio.py --check interview-prep   # report only
python3 tools/restyle_drawio.py interview-prep           # restyle in place
```

For each file, the script runs two checks and leaves the file untouched if either fails:

1. **Round trip:** it reads the draw.io model back and re-renders it in the theme the file was made in. The result must match the file exactly, which proves the reader understood every shape.
2. **Words:** every word of every label must still be there after restyling.

Running the script again on restyled files changes nothing.

## Checking a diagram

Render the SVG to PNG and look at it before committing (Playwright and Chromium are available). Overflowing labels and crowded arrows only show up in the picture.
