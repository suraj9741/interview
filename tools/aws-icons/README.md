# AWS Architecture Icons (vendored subset)

These SVGs are the official **AWS Architecture Icons**, copied from the npm package
[`aws-icons`](https://www.npmjs.com/package/aws-icons) v3.3.0 (MIT-licensed repackaging of the AWS icon set)
and renamed to short names. AWS allows these icons to be used in architecture diagrams.

`tools/drawio_svg.py` embeds them as base64 images (`box(..., icon="ec2-instance")` or `icon(...)`),
so each `.drawio.svg` is self-contained: GitHub renders the icons and draw.io can still edit the diagram.

To add an icon: copy another SVG from the package into this folder with a short kebab-case name,
then use that name in a generator script.
