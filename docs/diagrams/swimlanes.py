#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Turn the subgraphs of a rendered Mermaid flowchart SVG into swimlanes.

Mermaid sizes each subgraph to its nodes and centres its title on top. This
script gives every subgraph the same left and right edge, stacks them without a
gap, adds a header band at the left and writes the subgraph's title into it,
rotated by 90 degrees. Fill and stroke of each band come from the subgraph's
own style.

Run it on the SVG right after rendering, since rendering overwrites it:

  bash mermaid-render.sh docs/diagrams/bmad-flow.mmd
  python3 docs/diagrams/swimlanes.py docs/diagrams/bmad-flow.svg
"""

import argparse
import re
import sys
from pathlib import Path

HEADER = 40  # width of the header band holding the rotated title
FONT = "'trebuchet ms', verdana, arial, sans-serif"

CLUSTER = re.compile(
    r'(<g class="cluster"[^>]*>)<rect style="(?P<style>[^"]*)" x="(?P<x>[-\d.]+)" y="(?P<y>[-\d.]+)" '
    r'width="(?P<w>[-\d.]+)" height="(?P<h>[-\d.]+)"/>'
    r'<g class="cluster-label"[^>]*>.*?<p>(?P<title>[^<]*)</p>.*?</g></g>',
    re.S,
)


def style_value(style: str, key: str, default: str) -> str:
    m = re.search(rf"(?:^|;){key}:\s*([^;!]+)", style)
    return m.group(1).strip() if m else default


def lanes(svg: str) -> str:
    found = list(CLUSTER.finditer(svg))
    if not found:
        raise ValueError("no subgraph found")
    left = min(float(m["x"]) for m in found) - HEADER
    right = max(float(m["x"]) + float(m["w"]) for m in found)
    width = right - left
    # stacked without a gap: each lane reaches down to the top of the next one
    tops = sorted(float(m["y"]) for m in found)
    bottom = max(float(m["y"]) + float(m["h"]) for m in found)

    def lane(m: re.Match) -> str:
        y = float(m["y"])
        below = [t for t in tops if t > y]
        h = (below[0] if below else bottom) - y
        stroke = style_value(m["style"], "stroke", "#8a96a3")
        cx, cy = left + HEADER / 2, y + h / 2
        return (
            f'{m.group(1)}<rect style="{m["style"]}" x="{left}" y="{y}" width="{width}" height="{h}"/>'
            f'<rect x="{left}" y="{y}" width="{HEADER}" height="{h}" style="fill:{stroke};stroke:{stroke}"/>'
            f'<text transform="translate({cx} {cy}) rotate(-90)" text-anchor="middle" dominant-baseline="central" '
            f'style="fill:#ffffff;font-family:{FONT};font-size:16px;font-weight:bold">{m["title"]}</text></g>'
        )

    svg = CLUSTER.sub(lane, svg)

    vb = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"', svg)
    x0, y0, w0, h0 = (float(v) for v in vb.groups())
    new_x0 = min(x0, left - 8)
    new_w = max(x0 + w0, right + 8) - new_x0
    svg = svg.replace(vb.group(0), f'viewBox="{new_x0} {y0} {new_w} {h0}"', 1)
    return re.sub(r"max-width: [\d.]+px", f"max-width: {new_w:.1f}px", svg, count=1)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("svg", nargs="+", type=Path)
    args = p.parse_args()
    for path in args.svg:
        try:
            path.write_text(lanes(path.read_text()))
        except ValueError as e:
            print(f"{path}: {e}", file=sys.stderr)
            return 1
        print(f"{path}: swimlanes applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
