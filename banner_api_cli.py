#!/usr/bin/env python3
"""
AI Banner Generator (API) - Command Line Interface

One happy path: collect event data + speaker photo + logos on the CLI, fill the
design brief prompt, and let an image-generation API (OpenAI gpt-image-2 or Google
Gemini) produce the entire banner. The finished 1200x675 image is written to disk.

This is separate from banner_cli.py (the GIMP template path), which is unchanged.

Usage:
    banner_api_cli.py -o ./out --title1 "Café con IA" --speaker-name "Jane Doe" \
                      --date "Jun 12" --time "7 PM" --photo jane.jpg --logo aicdmx.png

API keys come from the environment (use direnv / .env):
    OPENAI_API_KEY, GEMINI_API_KEY (or GOOGLE_API_KEY)
OpenAI-compatible custom endpoints are supported with OPENAI_BASE_URL; if
OPENAI_API_KEY is unset, CLIPROXY_API_KEY / CLIPROXY_BASE_URL are also read from
~/.config/claude-aliases/env.

See docs/api-cli.md for full documentation.
"""

import argparse
import os
import re
import sys
from pathlib import Path

from banner_auto import BannerGeneratorAuto

PROMPTS_FILE = Path(__file__).parent / "prompts" / "banner_generation_prompts.md"


def load_design_brief() -> str:
    """Extract the 'Prompt 1' design brief from the prompts markdown file."""
    text = PROMPTS_FILE.read_text(encoding="utf-8")
    # Grab everything from the "## Prompt 1" heading up to the next "## Prompt" heading.
    match = re.search(r"^## Prompt 1\b.*?(?=^## Prompt 2\b)", text,
                      re.DOTALL | re.MULTILINE)
    brief = match.group(0).strip() if match else text.strip()
    return brief


def derive_logo_label(path: str) -> str:
    """Best-effort human label from a logo filename (used when no LABEL= is given)."""
    stem = Path(path).stem
    stem = re.sub(r"\(.*?\)", "", stem)                 # drop "(1024 × 1024 px)" etc.
    stem = re.sub(r"[-_]+", " ", stem)                  # separators -> spaces
    # Drop common descriptor words that aren't part of the brand name.
    drop = {"logo", "transparent", "blanco", "negro", "color", "white", "black",
            "png", "svgrepo", "com", "variacion", "px"}
    words = [w for w in stem.split() if w.lower() not in drop and not w.isdigit()]
    return " ".join(words).strip() or Path(path).stem


def build_prompt(args, design_brief: str) -> str:
    """Combine the event data, the design brief, and explicit preservation rules."""
    fields = [
        ("Title", args.title1),
        ("Subtitle", args.subtitle),
        ("Date", args.date),
        ("Time", args.time),
        ("Speaker name", args.speaker_name),
        ("Speaker role", args.speaker_title),
        ("Location / format", args.location),
    ]
    event_lines = "\n".join(f"- {label}: {value}" for label, value in fields if value)

    # Reference images are sent in this order: optional source banner, speaker photo,
    # then each logo. Enumerate them so the model knows which reference is which.
    logos = args.logo_specs or []
    ref_lines = []
    idx = 1
    if getattr(args, "from_banner", None):
        ref_lines.append(f"- Reference image {idx}: an existing 16:9 banner for this SAME "
                         f"event — match its style, colors, typography, and theme so this "
                         f"belongs to the same AI CDMX series.")
        idx += 1
    if args.photo:
        ref_lines.append(f"- Reference image {idx}: the speaker photo.")
        idx += 1
    for spec in logos:
        ref_lines.append(f"- Reference image {idx}: the \"{spec['label']}\" logo.")
        idx += 1
    refs_block = "\n".join(ref_lines) if ref_lines else "No reference images provided."

    if logos:
        logo_names = ", ".join(f'"{s["label"]}"' for s in logos)
        logo_rules = f"""- LOGOS — this is mandatory: place ALL {len(logos)} provided logos ({logo_names}) in a
  single clean horizontal row along the BOTTOM, inside the safe zone, evenly spaced and
  clearly separated. Reproduce each logo from its reference image as closely as possible —
  exact wordmark, shapes, and colors — legible and undistorted. Do NOT omit any logo, do
  NOT merge them together, and do NOT invent or add any other brand marks or icons.
  White/transparent logos should sit on the dark background as-is."""
    else:
        logo_rules = "- Do not add any logos or brand marks."

    if args.square:
        size_rule = ("- Produce ONE finished SQUARE banner, 1:1, 1080x1080 px.\n"
                     "- This is a square recomposition for social. DO NOT simply crop the "
                     "16:9 banner: recompose the layout for a square — increase the title "
                     "size, simplify the composition, prioritize visual impact, and remove "
                     "low-priority elements. It must still clearly belong to the AI CDMX series.")
    else:
        size_rule = "- Produce ONE finished banner, 16:9, 1200x675 px."

    preservation = f"""
EVENT INFORMATION (use this exact text in the banner):
{event_lines}

REFERENCE IMAGES (in order):
{refs_block}

OUTPUT REQUIREMENTS:
{size_rule}
- Render all event text legibly in the image, spelled exactly as given above.
- Use the EXACT speaker photo provided; do not replace, redraw, or alter the person's face.
  You may crop, cut out the background, blend edges, or stylize the framing only.
{logo_rules}
- Do not add extra text beyond the event information above.
"""
    return f"{design_brief}\n\n{preservation.strip()}\n"


def resolve_refs(args) -> list:
    """Return ordered reference image paths: source banner, speaker photo, then logos."""
    refs = []
    if getattr(args, "from_banner", None):
        refs.append(args.from_banner)
    if args.photo:
        refs.append(args.photo)
    refs.extend(spec["path"] for spec in (args.logo_specs or []))
    return refs


def main():
    parser = argparse.ArgumentParser(
        description="Generate a complete event banner with an image-generation API "
                    "(OpenAI gpt-image-2 or Google Gemini).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (no API call, no key needed) - prints the assembled prompt
  %(prog)s --dry-run -o ./out --title1 "Café con IA" --speaker-name "Jane Doe" \\
           --date "Jun 12" --photo jane.jpg --logo aicdmx.png

  # Generate with OpenAI (default backend)
  %(prog)s -o ./out --title1 "Café con IA" --subtitle "An evening with..." \\
           --speaker-name "Jane Doe" --speaker-title "AI Researcher" \\
           --date "Jun 12" --time "7 PM" --location "CDMX" \\
           --photo jane.jpg --logo aicdmx.png

  # Generate with Gemini
  %(prog)s --backend gemini -o ./out --title1 "Café con IA" \\
           --speaker-name "Jane Doe" --date "Jun 12" --photo jane.jpg

See docs/api-cli.md for full documentation.
        """,
    )

    parser.add_argument("--output-dir", "-o", required=True, metavar="DIR",
                        help="Output directory for the generated banner")
    parser.add_argument("--title1", required=True, metavar="TEXT",
                        help="Main title text")
    parser.add_argument("--subtitle", default="", metavar="TEXT",
                        help="Subtitle text")
    parser.add_argument("--date", required=True, metavar="TEXT",
                        help='Event date (flexible: "Jun 12", "2026-06-12", etc.)')
    parser.add_argument("--time", default="6-8PM", metavar="TEXT",
                        help='Event time (default: "6-8PM")')
    parser.add_argument("--speaker-name", default="", metavar="TEXT",
                        help="Speaker name")
    parser.add_argument("--speaker-title", default="", metavar="TEXT",
                        help="Speaker role/affiliation")
    parser.add_argument("--location", default="", metavar="TEXT",
                        help="Location / format (e.g. venue, online)")
    parser.add_argument("--photo", metavar="FILE",
                        help="Speaker photo, used as a reference image")
    parser.add_argument("--logo", action="append", default=[], metavar="[LABEL=]FILE",
                        help="Logo image used as a reference (repeatable: AI CDMX + partners). "
                             "Optionally prefix a label so the prompt can name it, e.g. "
                             "--logo \"Cultura UAM=/path/uam.png\". Without a label, one is "
                             "derived from the filename.")

    parser.add_argument("--backend", choices=["gemini", "openai"], default="openai",
                        help="Image API backend (default: openai)")
    parser.add_argument("--square", action="store_true",
                        help="Produce a 1:1 square (1080x1080) recomposition instead of 16:9. "
                             "Pair with --from-banner to recompose an existing banner.")
    parser.add_argument("--from-banner", metavar="FILE", dest="from_banner",
                        help="Existing banner image to use as a style reference (e.g. the "
                             "16:9 version when generating a --square so it matches the series)")
    parser.add_argument("--model", default=None, metavar="NAME",
                        help="Override the backend's default model")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the assembled prompt, references, and output path; "
                             "do not call the API (no key required)")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress non-error output")

    args = parser.parse_args()

    # Validate input files exist.
    if args.photo:
        args.photo = str(Path(args.photo).resolve())
        if not os.path.exists(args.photo):
            print(f"Error: Speaker photo not found: {args.photo}", file=sys.stderr)
            sys.exit(1)
    if args.from_banner:
        args.from_banner = str(Path(args.from_banner).resolve())
        if not os.path.exists(args.from_banner):
            print(f"Error: --from-banner image not found: {args.from_banner}", file=sys.stderr)
            sys.exit(1)
    args.logo_specs = []
    for logo in args.logo:
        # Optional "Label=path" syntax; otherwise derive a label from the filename.
        if "=" in logo:
            label, raw_path = logo.split("=", 1)
            label = label.strip()
        else:
            label, raw_path = "", logo
        p = str(Path(raw_path).resolve())
        if not os.path.exists(p):
            print(f"Error: Logo not found: {raw_path}", file=sys.stderr)
            sys.exit(1)
        if not label:
            label = derive_logo_label(p)
        args.logo_specs.append({"label": label, "path": p})

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build output filename, reusing the shared date/slug helpers.
    gen = BannerGeneratorAuto()
    parsed_date = gen.parse_date_from_text(args.date)
    title_slug = gen.slugify(args.title1, 10)
    date_part = parsed_date if parsed_date else "banner"
    shape = "square" if args.square else "16x9"
    out_path = str(output_dir / f"{date_part}-{title_slug}-{args.backend}-{shape}.png")

    # Assemble the prompt.
    design_brief = load_design_brief()
    prompt = build_prompt(args, design_brief)
    refs = resolve_refs(args)

    if args.dry_run:
        print("=== DRY RUN (no API call) ===")
        print(f"Backend:     {args.backend}")
        print(f"Model:       {args.model or '(provider default)'}")
        print(f"Output:      {out_path}")
        print(f"References:  {refs if refs else '(none)'}")
        print("\n=== PROMPT ===")
        print(prompt)
        return 0

    import image_apis

    if not args.quiet:
        print(f"Generating banner via {args.backend}...")
        print(f"  Title:  {args.title1}")
        print(f"  Refs:   {len(refs)} image(s)")
        print(f"  Output: {out_path}")

    try:
        image_apis.generate(args.backend, prompt, refs, out_path, model=args.model,
                            aspect=("1:1" if args.square else "16:9"))
    except image_apis.ProviderError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error generating banner: {e}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"Done! Banner written to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
