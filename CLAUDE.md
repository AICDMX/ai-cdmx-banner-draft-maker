# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Event banner generator for AI CDMX. Two paths:

1. **API path (PRIMARY)** — `banner_api_cli.py`: event data + speaker photo + logos →
   an image-generation API (OpenAI `gpt-image-2` via the Responses API, or Google Gemini
   `gemini-3.x` image models) produces the whole banner (16:9 1200×675 or square 1:1
   1080×1080). Needs `pip install -e .[api]` and API keys from the env (direnv / `.env`).
   Full docs: **`docs/api-cli.md`**.
2. **GIMP path (legacy)** — Python/Tkinter GUI + `banner_cli.py` that populate GIMP `.xcf`
   templates and export `.xcf` + `.jpg`. Kept for pixel-exact logo/photo placement.

## Commands

```bash
# --- API path (primary) ---
pip install -e .[api]            # openai, google-genai, pillow (one-time)
cp .env.example .env && direnv allow   # add OPENAI_API_KEY / GEMINI_API_KEY

# What to pass in: event fields + --photo + AI CDMX logo + the combined partner strip
python3 banner_api_cli.py -o ./out --backend openai \
    --title1 "Event" --subtitle "..." \
    --speaker-name "Name" --speaker-title "Role" \
    --date "Aug 18" --time "6 PM" --location "Presencial + YouTube en vivo · CDMX" \
    --photo "/path/to/speaker.png" \
    --logo "AI CDMX=~/Dropbox/events/ia-cdmx/Visual Assets/Logos/AI CDMX transparent logo (1024 × 1024 px).png" \
    --logo "partners=~/Dropbox/events/ia-cdmx/Visual Assets/casa-rafael-galvan/partner-logos-strip-blanco.png"
# add --square --from-banner <16x9.png> for the 1:1 social version
# add --dry-run to preview the prompt without an API call (no key needed)

# Rebuild the partner-logo strip from source logos (tools/build_partner_strip.py)
python3 tools/build_partner_strip.py -o partners.png logoA.png logoB.png ...

# --- GIMP path (legacy) ---
make run          # Run the GUI application (verifies prerequisites first)
make run-auto     # Run in auto mode using saved config (no GUI)
make check        # Verify Python, tkinter, and GIMP are installed
make clean        # Remove __pycache__, .pyc files, pytest/mypy caches
python3 banner_cli.py -T ".../Templates/" -o ".../Automated/" \
    --title1 "Event" --speaker-name "Name" --date "Jan 15" --time "7 PM"
```

Note: `make lint`, `make format`, and `make test` are placeholders (not configured).

## Architecture

```
# API path (primary)
banner_api_cli.py      # API CLI - event data + photo + logos -> full banner (see docs/api-cli.md)
image_apis.py          # OpenAI (Responses API + image_generation tool) & Gemini providers; cover-fit
prompts/               # Design-brief prompts injected into the API call
tools/build_partner_strip.py  # Combine partner logos into one strip for reliable placement

# GIMP path (legacy)
banner_gui.py          # GUI entry point - launches Tkinter interface
banner_cli.py          # CLI entry point - command-line arguments (see docs/cmdline.md)
banner_gui_tk.py       # Tkinter GUI (1200+ lines) - form, file dialogs, config persistence
banner_auto.py         # Shared generation logic - date parsing, file naming, GIMP execution
                       # (the API CLI reuses its date-parsing / slug / naming helpers)
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
