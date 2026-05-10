# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GIMP Banner Generator - A GUI tool for generating event banners from GIMP templates with automated text and image placement. Uses Python/Tkinter interface to populate GIMP `.xcf` templates and export both `.xcf` and `.png` versions.

## Commands

```bash
make run          # Run the GUI application (verifies prerequisites first)
make run-auto     # Run in auto mode using saved config (no GUI)
make check        # Verify Python, tkinter, and GIMP are installed
make clean        # Remove __pycache__, .pyc files, pytest/mypy caches

# CLI usage (see docs/cmdline.md for full documentation)
python3 banner_cli.py \
    -T "~/Dropbox/events/ia-cdmx/Visual Assets/Banners/Templates/" \
    -o "~/Dropbox/events/ia-cdmx/Visual Assets/Banners/Automated/" \
    --title1 "Event" --speaker-name "Name" --date "Jan 15" --time "7 PM"
```

Note: `make lint`, `make format`, and `make test` are placeholders (not configured).

## Architecture

```
banner_gui.py          # GUI entry point - launches Tkinter interface
banner_cli.py          # CLI entry point - command-line arguments (see docs/cmdline.md)
banner_gui_tk.py       # Tkinter GUI (1200+ lines) - form, file dialogs, config persistence
banner_auto.py         # Shared generation logic - date parsing, file naming, GIMP execution
gimp_scripts_gimp3.py  # Generates Python-Fu scripts for GIMP 3.0
gimp_scripts/          # GIMP script templates (Jinja-style variable substitution)
```

**Flow**: GUI/CLI collects user input → `banner_auto.py` orchestrates → `gimp_scripts_gimp3.py` generates Python-Fu script → script runs headless GIMP → updates text layers + inserts photo → exports XCF/JPG

## Key Technical Details

- **GIMP 3.0 only** - Uses GObject Introspection API, explicitly rejects GIMP 2.x
- **Zero external dependencies** - Only Python stdlib + system packages (tkinter, GIMP)
- **Config persistence** - Saves to `~/.config/gimp-banner-generator/config.json`
- **Headless execution** - Supports `xvfb-run` for systems without DISPLAY
- **Date parsing** - Handles many formats with intelligent year guessing (see `banner_auto.py:parse_date_for_filename`)

## Template Requirements

GIMP templates must have these exact layer names (case-sensitive):
- **Text layers**: `Title1`, `Title2`, `SpeakerName`, `SpeakerTitle`, `Date`, `Time`
- **Photo placeholder**: `SpeakerPhoto` (regular layer, positioned/sized for photo insertion)

## Paths

- **Templates**: `~/Dropbox/events/ia-cdmx/Visual Assets/Banners/Templates/` — contains `Banner.xcf` and `Square.xcf`
- **Output**: `~/Dropbox/events/ia-cdmx/Visual Assets/Banners/Automated/`

## Output Naming

Pattern: `{parsed_date}-{title_slug}-{template_slug}.xcf/jpg`

- **parsed_date**: Date extracted from `--date` input via flexible parsing (e.g. `2026-02-20`)
- **title_slug**: First 10 chars of `--title1`, lowercased, special chars replaced with dashes
- **template_slug**: First 10 chars of template filename stem (e.g. `banner`, `square`)

Example: `--title1 "Cariño en" --date "Jan 20"` with `Banner.xcf` → `2026-01-20-cari-o-en-banner.xcf`
