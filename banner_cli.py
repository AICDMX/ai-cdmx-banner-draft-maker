#!/usr/bin/env python3
"""
GIMP Banner Generator - Command Line Interface

Standalone CLI for generating banners without the GUI.
Uses the same generation logic as the GUI version.

Usage:
    banner_cli.py --template t.xcf --output-dir ./out --title1 "Event" \
                  --speaker-name "John Doe" --date "Jan 15" --time "7:00 PM"
"""

import argparse
import os
import sys
from pathlib import Path

from banner_auto import BannerGeneratorAuto


def main():
    parser = argparse.ArgumentParser(
        description='Generate event banners from GIMP templates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single template
  %(prog)s -t templates/banner.xcf -o ./output --title1 "AI Meetup" \\
           --speaker-name "Jane Doe" --date "Feb 20" --time "7:00 PM"

  # Multiple templates
  %(prog)s -t templates/wide.xcf templates/square.xcf -o ./output \\
           --title1 "AI Meetup" --speaker-name "Jane Doe" \\
           --date "Feb 20" --time "7:00 PM"

  # All templates in a directory
  %(prog)s -T templates/ -o ./output --title1 "AI Meetup" \\
           --speaker-name "Jane Doe" --date "Feb 20" --time "7:00 PM"

  # With all options
  %(prog)s -t banner.xcf -o ./out --title1 "Main Title" --title2 "Subtitle" \\
           --speaker-name "John Doe" --speaker-title "CEO, Company" \\
           --date "March 15, 2025" --time "6:30 PM" --photo speaker.jpg

See docs/cmdline.md for full documentation.
        """
    )

    # Template arguments (at least one of --template or --template-dir required)
    parser.add_argument('--template', '-t', nargs='+', metavar='FILE',
                       help='GIMP template file(s) (.xcf)')
    parser.add_argument('--template-dir', '-T', metavar='DIR',
                       help='Directory containing .xcf templates (all will be used)')
    parser.add_argument('--output-dir', '-o', required=True, metavar='DIR',
                       help='Output directory for generated files')
    parser.add_argument('--title1', required=True, metavar='TEXT',
                       help='Main title text')
    parser.add_argument('--speaker-name', required=True, metavar='TEXT',
                       help='Speaker name')
    parser.add_argument('--date', required=True, metavar='TEXT',
                       help='Event date (flexible format: "Jan 15", "2025-01-15", etc.)')
    parser.add_argument('--time', default='6-8PM', metavar='TEXT',
                       help='Event time (default: "6-8PM")')

    # Optional arguments
    parser.add_argument('--title2', default='', metavar='TEXT',
                       help='Subtitle text')
    parser.add_argument('--speaker-title', default='', metavar='TEXT',
                       help='Speaker title/affiliation')
    parser.add_argument('--photo', metavar='FILE',
                       help='Speaker photo file')

    # Output control
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress non-error output')
    parser.add_argument('--version', '-v', action='version', version='%(prog)s 1.0')

    args = parser.parse_args()

    if not args.template and not args.template_dir:
        parser.error('at least one of --template/-t or --template-dir/-T is required')

    # Validate paths
    templates = []

    if args.template_dir:
        td = Path(args.template_dir).resolve()
        if not td.is_dir():
            print(f"Error: Template directory not found: {args.template_dir}", file=sys.stderr)
            sys.exit(1)
        found = sorted(td.glob('*.xcf'))
        if not found:
            print(f"Error: No .xcf files found in {td}", file=sys.stderr)
            sys.exit(1)
        templates.extend(found)

    for t in (args.template or []):
        t_path = Path(t).resolve()
        if not t_path.exists():
            print(f"Error: Template not found: {t}", file=sys.stderr)
            sys.exit(1)
        if not t_path.suffix.lower() == '.xcf':
            print(f"Error: Template must be .xcf file: {t}", file=sys.stderr)
            sys.exit(1)
        templates.append(t_path)

    output_dir = Path(args.output_dir).resolve()
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        if not args.quiet:
            print(f"Created output directory: {output_dir}")

    photo_path = ''
    if args.photo:
        photo_path = str(Path(args.photo).resolve())
        if not os.path.exists(photo_path):
            print(f"Error: Photo not found: {args.photo}", file=sys.stderr)
            sys.exit(1)

    # Use BannerGeneratorAuto for generation logic
    generator = BannerGeneratorAuto()

    # Parse date for filename
    parsed_date = generator.parse_date_from_text(args.date)
    title_slug = generator.slugify(args.title1, 10)

    generated_count = 0
    failed_count = 0

    for template_path in templates:
        template_slug = generator.slugify(template_path.stem, 10)

        if parsed_date:
            base_filename = f"{parsed_date}-{title_slug}-{template_slug}"
        else:
            base_filename = f"banner-{title_slug}-{template_slug}"

        output_xcf = str(output_dir / f"{base_filename}.xcf")
        output_jpg = str(output_dir / f"{base_filename}.jpg")

        if not args.quiet:
            print(f"Generating from: {template_path.name}")
            print(f"  Output: {base_filename}.xcf, {base_filename}.jpg")

        try:
            generator.update_banner(
                template_path=str(template_path),
                title1=args.title1,
                title2=args.title2,
                speaker_name=args.speaker_name,
                speaker_title=args.speaker_title,
                date=args.date,
                time=args.time,
                photo_path=photo_path,
                output_xcf=output_xcf,
                output_jpg=output_jpg
            )
            generated_count += 1
            if not args.quiet:
                print(f"  Done!")

        except Exception as e:
            print(f"Error generating {template_path.name}: {e}", file=sys.stderr)
            failed_count += 1

    # Summary
    if not args.quiet:
        print()
        print(f"Generated {generated_count}/{len(templates)} banner(s)")
        if failed_count > 0:
            print(f"Failed: {failed_count}")

    sys.exit(1 if failed_count > 0 else 0)


if __name__ == "__main__":
    main()
