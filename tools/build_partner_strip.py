#!/usr/bin/env python3
"""
Build a combined partner-logo strip for the API banner generator.

Lays out multiple logos in a single horizontal row on a transparent background,
normalized to a common height. Passing this ONE pre-arranged strip to
banner_api_cli.py (as a single --logo) gets the image model to place the partner
logos far more reliably than handing it each mark separately.

Usage:
    python3 tools/build_partner_strip.py -o partners.png LOGO1 LOGO2 LOGO3 ...
    python3 tools/build_partner_strip.py -o partners.png --height 300 --gap 120 a.png b.png

Requires Pillow (pip install -e .[api]).
"""

import argparse
import sys
from pathlib import Path


def build_strip(logo_paths, out_path, *, height=300, gap=120, pad=40):
    from PIL import Image

    imgs = []
    for p in logo_paths:
        im = Image.open(p).convert("RGBA")
        w, h = im.size
        imgs.append(im.resize((round(w * height / h), height), Image.LANCZOS))

    total_w = sum(i.width for i in imgs) + gap * (len(imgs) - 1) + pad * 2
    strip = Image.new("RGBA", (total_w, height + pad * 2), (0, 0, 0, 0))
    x = pad
    for im in imgs:
        strip.alpha_composite(im, (x, pad))
        x += im.width + gap
    strip.save(out_path)
    return out_path, strip.size


def main():
    ap = argparse.ArgumentParser(description="Combine logos into one horizontal strip (transparent bg).")
    ap.add_argument("logos", nargs="+", metavar="LOGO", help="Logo image paths, left to right")
    ap.add_argument("-o", "--output", required=True, metavar="FILE", help="Output PNG path")
    ap.add_argument("--height", type=int, default=300, help="Normalized logo height in px (default 300)")
    ap.add_argument("--gap", type=int, default=120, help="Transparent gap between logos in px (default 120)")
    ap.add_argument("--pad", type=int, default=40, help="Outer padding in px (default 40)")
    args = ap.parse_args()

    for p in args.logos:
        if not Path(p).exists():
            print(f"Error: logo not found: {p}", file=sys.stderr)
            sys.exit(1)

    try:
        out, size = build_strip(args.logos, args.output,
                                height=args.height, gap=args.gap, pad=args.pad)
    except ImportError:
        print("Error: Pillow is required. Run: pip install -e .[api]", file=sys.stderr)
        sys.exit(1)
    print(f"Wrote {out} ({size[0]}x{size[1]}) from {len(args.logos)} logos")


if __name__ == "__main__":
    main()
