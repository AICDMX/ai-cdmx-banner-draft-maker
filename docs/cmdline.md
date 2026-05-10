# Command Line Interface

The GIMP Banner Generator can be used entirely from the command line without launching the GUI.

## Quick Start

```bash
python3 banner_cli.py \
    --template templates/banner.xcf \
    --output-dir ./output \
    --title1 "AI Meetup CDMX" \
    --speaker-name "Jane Doe" \
    --date "Feb 20" \
    --time "7:00 PM"
```

## Usage

```
banner_cli.py --template FILE [FILE ...] --output-dir DIR --title1 TEXT
              --speaker-name TEXT --date TEXT --time TEXT
              [--title2 TEXT] [--speaker-title TEXT] [--photo FILE]
              [--quiet] [--help] [--version]
```

## Required Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--template` | `-t` | GIMP template file(s) (.xcf). Can specify multiple. |
| `--output-dir` | `-o` | Output directory for generated files |
| `--title1` | | Main title text |
| `--speaker-name` | | Speaker name |
| `--date` | | Event date (flexible format) |
| `--time` | | Event time |

## Optional Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--title2` | | Subtitle text |
| `--speaker-title` | | Speaker title/affiliation |
| `--photo` | | Speaker photo file |
| `--quiet` | `-q` | Suppress non-error output |
| `--version` | `-v` | Show version |
| `--help` | `-h` | Show help message |

## Date Formats

The `--date` argument accepts many formats:

- `2025-01-15` - ISO format
- `01/15/2025` - US format
- `Jan 15` - Month name (year auto-detected)
- `January 15, 2025` - Full month name with year
- `15 Jan` - Day first
- `15th January 2025` - Ordinal day

When year is omitted, the system assumes the nearest future occurrence.

## Examples

### Single Template

```bash
python3 banner_cli.py \
    -t templates/banner.xcf \
    -o ./output \
    --title1 "Machine Learning Workshop" \
    --speaker-name "Dr. Smith" \
    --date "March 20" \
    --time "6:30 PM"
```

### Multiple Templates

Generate banners from multiple templates at once:

```bash
python3 banner_cli.py \
    -t templates/wide.xcf templates/square.xcf templates/story.xcf \
    -o ./output \
    --title1 "AI Meetup" \
    --speaker-name "Jane Doe" \
    --date "Feb 20" \
    --time "7:00 PM"
```

### Full Options

```bash
python3 banner_cli.py \
    --template templates/banner.xcf \
    --output-dir ./output \
    --title1 "Introduction to Neural Networks" \
    --title2 "A Beginner's Guide" \
    --speaker-name "Dr. Maria Garcia" \
    --speaker-title "AI Research Lead, TechCorp" \
    --date "April 15, 2025" \
    --time "7:00 PM" \
    --photo ./photos/maria.jpg
```

### Quiet Mode (for scripts)

```bash
python3 banner_cli.py -q \
    -t templates/banner.xcf \
    -o ./output \
    --title1 "Event" \
    --speaker-name "Speaker" \
    --date "Jan 1" \
    --time "7 PM"
```

## Output Files

For each template, two files are generated:

- `YYYY-MM-DD-{title}-{template}.xcf` - Editable GIMP file
- `YYYY-MM-DD-{title}-{template}.jpg` - Export-ready image

Example: `2025-02-20-ai-meetup-banner.xcf`

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - all banners generated |
| 1 | Failure - one or more banners failed |

## Using with Make

```bash
make run-cli ARGS="--template t.xcf -o ./out --title1 'Event' --speaker-name 'Name' --date 'Jan 1' --time '7 PM'"
```

## Comparison: GUI vs CLI vs Auto Mode

| Feature | GUI | CLI | Auto (`--auto`) |
|---------|-----|-----|-----------------|
| Entry point | `banner_gui.py` | `banner_cli.py` | `banner_gui.py --auto` |
| Config source | Interactive form | Command-line args | Saved config file |
| Use case | First-time setup, visual preview | Scripting, automation | Repeat last generation |

## Troubleshooting

### GIMP not found

Ensure GIMP 3.0+ is installed and in your PATH:

```bash
gimp --version
```

### Display errors (headless)

If running without a display server, install xvfb:

```bash
# Arch
sudo pacman -S xorg-server-xvfb

# Ubuntu/Debian
sudo apt install xvfb
```

The tool will automatically use `xvfb-run` when needed.

### Template layer errors

Ensure your template has the required layer names (case-sensitive):
- `Title1`, `Title2`, `SpeakerName`, `SpeakerTitle`, `Date`, `Time`
- `SpeakerPhoto` (for photo placement)
