# AI Banner Generator (API) — `banner_api_cli.py`

**This is the primary, recommended way to make event banners.** You provide the event text,
the speaker photo, and logos on the command line; an image-generation API (OpenAI
`gpt-image-2` or Google Gemini) produces the whole banner — 16:9 (1200×675) or square 1:1
(1080×1080).

The older GIMP template path (`banner_cli.py`) still works and is kept for pixel-exact
logos/photo, but the API path is what we use day to day.

## What to pass in (AI CDMX events)

The proven invocation — speaker photo + AI CDMX logo + the **combined partner-logo strip**:

```bash
python3 banner_api_cli.py -o ./out --backend openai \
  --title1     "Eclipses en Agujeros Negros" \
  --subtitle   "Detectándolos con Redes Neuronales y Machine Learning" \
  --speaker-name  "Dr. Gustavo Magallanes-Guijón" \
  --speaker-title "Senior Scientific Computing Architect" \
  --date "Aug 18" --time "6 PM" \
  --location "Presencial + YouTube en vivo · CDMX" \
  --photo "/path/to/speaker.png" \
  --logo  "AI CDMX=$HOME/Dropbox/events/ia-cdmx/Visual Assets/Logos/AI CDMX transparent logo (1024 × 1024 px).png" \
  --logo  "partner logos in a row (UAM, Cultura UAM, Casa Rafael Galván, YouTube)=$HOME/Dropbox/events/ia-cdmx/Visual Assets/casa-rafael-galvan/partner-logos-strip-blanco.png"
```

Then make the square version from that banner so it stays on-series. 
**Note:** Pass all the same args (title, photo, logos) along with `--from-banner`:

```bash
python3 banner_api_cli.py --square -o ./out --backend openai \
  --from-banner ./out/2026-08-18-eclipses-e-openai-16x9.png \
  --title1 "Eclipses en Agujeros Negros" \
  --subtitle "Detectándolos con Redes Neuronales y Machine Learning" \
  --speaker-name "Dr. Gustavo Magallanes-Guijón" \
  --speaker-title "Senior Scientific Computing Architect" \
  --date "Aug 18" --time "6 PM" --location "Presencial + YouTube en vivo · CDMX" \
  --photo "/path/to/speaker.png" \
  --logo  "AI CDMX=$HOME/Dropbox/events/ia-cdmx/Visual Assets/Logos/AI CDMX transparent logo (1024 × 1024 px).png" \
  --logo  "partner logos in a row=$HOME/Dropbox/events/ia-cdmx/Visual Assets/casa-rafael-galvan/partner-logos-strip-blanco.png"
```

Key inputs, in short:
- **Speaker photo** → `--photo` (used as a reference; model keeps the person)
- **AI CDMX logo** → its own `--logo "AI CDMX=..."`
- **All partner/venue logos** → the prebuilt strip `--logo "...=.../partner-logos-strip-blanco.png"`
  (one tidy strip places far more reliably than separate marks — see *Partner logos* below)
- Use `--dry-run` first to preview the prompt without spending an API call.

## Install

The API path needs extra packages (the GIMP path stays zero-dependency):

```bash
pip install -e .[api]      # openai, google-genai, pillow
```

## API keys (direnv)

Keys are read from the environment:

- `OPENAI_API_KEY`
- `GEMINI_API_KEY` (or `GOOGLE_API_KEY`)

Setup with [direnv](https://direnv.net/):

```bash
cp .env.example .env        # then edit .env with your real keys
direnv allow                # loads .env into the shell in this directory
echo $GEMINI_API_KEY        # verify
```

`.env` is gitignored; `.envrc` and `.env.example` are committed.

## Usage

```bash
python3 banner_api_cli.py -o ./out \
    --title1 "Café con IA" \
    --subtitle "An evening with..." \
    --speaker-name "Jane Doe" \
    --speaker-title "AI Researcher" \
    --date "Jun 12" \
    --time "7 PM" \
    --location "CDMX" \
    --photo jane.jpg \
    --logo aicdmx.png --logo partner.png
```

### Arguments

| Flag | Required | Description |
|---|---|---|
| `--output-dir`, `-o` | yes | Output directory |
| `--title1` | yes | Main title |
| `--date` | yes | Event date (flexible: `Jun 12`, `2026-06-12`, …) |
| `--subtitle` | no | Subtitle |
| `--time` | no | Event time (default `6-8PM`) |
| `--speaker-name` | no | Speaker name |
| `--speaker-title` | no | Speaker role/affiliation |
| `--location` | no | Location / format |
| `--photo` | no | Speaker photo (used as a reference image) |
| `--logo` | no | Logo image (repeatable: AI CDMX + partners) |
| `--backend` | no | `gemini` (default) or `openai` |
| `--model` | no | Override the backend's default model |
| `--dry-run` | no | Print the assembled prompt/refs/output path; no API call, no key |
| `--quiet`, `-q` | no | Suppress non-error output |

### Models

| Backend | Default model | Notes |
|---|---|---|
| `gemini` | `gemini-3.1-flash-image-preview` | Native 16:9, fast/cheap; use `gemini-3-pro-image-preview` via `--model` for higher quality |
| `openai` | `gpt-5.5` (drives the `gpt-image-2` image tool) | Generates at `2048x1152`, cover-fit to 1200×675 |

### Output

`{date}-{title-slug}-{backend}.png` in the output directory, cover-fit to **1200×675**.
Date and slug use the same helpers as the GIMP CLI (`banner_auto.py`).

## How it works

1. Loads the design brief (Prompt 1) from `prompts/banner_generation_prompts.md`.
2. Injects the event fields and explicit preservation rules (use the exact speaker photo,
   keep logos legible, render text exactly, 16:9 1200×675).
3. Sends the prompt + reference images (speaker photo first, then logos) to the backend.
4. Saves the result and cover-fits it to 1200×675.

## Partner logos (combined strip)

Image models drop/distort logos when handed several separate marks. The reliable trick is
to pre-arrange the partner logos into **one horizontal strip** and pass that as a single
`--logo`, so the model only has to *place* it, not reconstruct and arrange each mark.

Build a strip with the helper:

```bash
python3 tools/build_partner_strip.py -o partners.png logoA.png logoB.png logoC.png
```

A prebuilt strip for Casa Rafael Galván events (UAM institutional + Cultura UAM + Casa
Rafael Galván + YouTube, white) lives with the source logos at:

```
~/Dropbox/events/ia-cdmx/Visual Assets/casa-rafael-galvan/partner-logos-strip-blanco.png
```

Use it as one reference, with the AI CDMX logo kept separate:

```bash
python3 banner_api_cli.py -o ./out --backend openai \
  --title1 "..." --speaker-name "..." --date "Aug 18" --time "6 PM" \
  --photo speaker.png \
  --logo "AI CDMX=.../Logos/AI CDMX transparent logo (1024 × 1024 px).png" \
  --logo "partner logos in a row (UAM, Cultura UAM, Casa Rafael Galván, YouTube)=.../casa-rafael-galvan/partner-logos-strip-blanco.png"
```

## Square (1:1) versions

`--square` produces a 1080×1080 **recomposition** (not a crop): bigger title, simplified
layout, per the brief's square rules. Pair with `--from-banner` to feed the finished 16:9
banner as a style reference so the square stays on-series.

**IMPORTANT:** You MUST pass all the same metadata (title, subtitle, speaker, photo, logos) 
along with `--from-banner`. The `--from-banner` provides style reference, but the logos and 
other elements won't appear unless you explicitly pass them again:

```bash
python3 banner_api_cli.py --square -o ./out --backend openai \
  --from-banner ./out/2026-08-18-...-16x9.png \
  --title1 "..." --speaker-name "..." --date "Aug 18" --photo speaker.png \
  --logo "AI CDMX=..." --logo "partners=.../partner-logos-strip-blanco.png"
```

**Wrong (logos will be missing):**
```bash
# ❌ This will produce a square banner WITHOUT logos
python3 banner_api_cli.py --square -o ./out --backend openai \
  --from-banner ./out/2026-08-18-...-16x9.png \
  --title1 "..." --date "Aug 18"
  # Missing: --photo, --logo flags
```

## Dry run (offline)

```bash
python3 banner_api_cli.py --dry-run -o ./out \
    --title1 "Café con IA" --speaker-name "Jane Doe" --date "Jun 12" \
    --photo jane.jpg --logo aicdmx.png
```

Prints the full assembled prompt, the reference list, and the planned output path without
calling the API or needing a key.
