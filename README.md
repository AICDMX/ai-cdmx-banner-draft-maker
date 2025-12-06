# GIMP Banner Generator

A GUI tool for generating event banners from GIMP templates with automated text and image placement.

## Overview

This tool provides a simple Python/Tkinter interface to:
- Select from a directory of GIMP `.xcf` templates
- Fill in event details (titles, speaker info, date/time, photo)
- Automatically populate the template using headless GIMP
- Export both `.xcf` (editable with layers) and `.png` (ready-to-use) versions
- Open the result in GIMP for manual touch-ups

## Prerequisites

- **Python**: 3.8 or higher
- **GIMP**: 2.10 or higher, installed and available on your system PATH
- **Platform**: Tested on Linux (Arch-based systems)
- **Dependencies**: Only Python standard library (no external packages required)

### Installing GIMP

On Arch Linux:
```bash
sudo pacman -S gimp
```

On Ubuntu/Debian:
```bash
sudo apt install gimp
```

Verify GIMP is on your PATH:
```bash
gimp --version
```

## Installation

### Using uv (Recommended)

This project uses `uv` for environment management:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone or navigate to the project directory
cd ai-cdmx-banner-draft-maker

# Run the tool (uv will handle the environment)
uv run banner_gui.py
```

### Direct Execution

If you prefer not to use uv:

```bash
# Make the script executable
chmod +x banner_gui.py

# Run directly
./banner_gui.py
```

Or:

```bash
python3 banner_gui.py
```

## How to Use

1. **Launch the GUI**:
   ```bash
   uv run banner_gui.py
   # or
   python3 banner_gui.py
   ```

2. **Select Template Directory**:
   - Click "Browse" next to "Template Directory"
   - Navigate to your folder containing `.xcf` templates
   - The tool will list all available templates

3. **Choose a Template**:
   - Select one from the list
   - Click "Refresh" if you add new templates while the app is running

4. **Select Output Directory**:
   - Click "Browse" next to "Output Directory"
   - Choose where you want to save the generated banners
   - The tool remembers your last selection during the session

5. **Fill in Event Details**:
   - **Title 1** (required): Main event title
   - **Title 2** (optional): Subtitle or additional info
   - **Speaker Name** (required): Name of the speaker
   - **Speaker Title** (optional): Speaker's role/title
   - **Date** (required): Event date in any human-readable format
     - Examples: `2025-12-31`, `Dec 31, 2025`, `31/12/2025`, `December 31st, 2025 at CDMX`
   - **Time** (required): Event time (free text, e.g., `7:00 PM MST`, `19:00`)
     - The tool remembers your last time value as a default
   - **Speaker Photo** (optional): Browse to select a `.jpg`, `.png`, or other image

6. **Generate Banner**:
   - Click "Generate & Open in GIMP"
   - The tool will:
     - Update all text layers in the template
     - Insert and scale the speaker photo (if provided)
     - Save both `.xcf` (editable) and `.png` (export-ready) versions
     - Open the `.xcf` file in GIMP for you to review and tweak

## Output Naming

Generated files are automatically named based on your inputs:

- **Format**: `YYYY-MM-DD-titleprefix.xcf` and `YYYY-MM-DD-titleprefix.png`
- **Date extraction**: The tool attempts to parse a date from your Date field using common formats
- **Title prefix**: The first 10 characters of Title 1, slugified (lowercase, special chars replaced with `-`)

**Examples**:
- Date: `Dec 31, 2025`, Title 1: `AI Workshop Series` → `2025-12-31-ai-worksho.xcf`
- Date: `2025-06-15 at Mexico City`, Title 1: `Neural Nets 101` → `2025-06-15-neural-net.xcf`
- Date: `Next Tuesday` (unparseable), Title 1: `Deep Dive` → `banner-deep-dive.xcf`

## Template Requirements

To create compatible GIMP templates, follow these guidelines:

### File Format
- Save templates as `.xcf` (GIMP's native format)
- Place all templates in a single directory for easy selection

### Required Text Layers

Your template **must** include these named text layers (right-click layer → Edit Layer Attributes to set the name):

| Layer Name      | Purpose                | Required |
|-----------------|------------------------|----------|
| `Title1`        | Main event title       | Yes      |
| `Title2`        | Subtitle/secondary info| Optional |
| `SpeakerName`   | Speaker's name         | Yes      |
| `SpeakerTitle`  | Speaker's role/title   | Optional |
| `Date`          | Event date             | Yes      |
| `Time`          | Event time             | Yes      |

**Important**: Layer names are case-sensitive. Use exactly these names.

### Speaker Photo Placeholder

For automatic photo placement, create a layer named `SpeakerPhoto`:

1. In GIMP, add a new layer: **Layer → New Layer**
2. Name it exactly `SpeakerPhoto`
3. Position and size this layer where you want the speaker photo to appear
4. The tool will:
   - Load the selected photo
   - Scale it to fit within this layer's dimensions (maintaining aspect ratio)
   - Center it within the placeholder area
   - Insert it as a new layer named `SpeakerPhoto_Inserted`

**Tips**:
- Make the placeholder layer slightly transparent so you can see the background while designing
- Size it to match your desired photo dimensions (e.g., 300x300px for a square headshot)
- The tool scales photos proportionally, so leave extra space if photos have varying aspect ratios

### Design Recommendations

- **Font sizes**: Use readable sizes (e.g., 48-72pt for titles, 24-36pt for body text)
- **Text alignment**: Center or left-align text layers for consistency
- **Layers**: Keep your template organized with named layers
- **Background**: Include a background layer with your branding/design
- **Guides**: Use GIMP guides to align text and photo consistently

### Example Template Structure

```
MyTemplate.xcf
├── Background (image/solid color)
├── Title1 (text layer)
├── Title2 (text layer)
├── SpeakerName (text layer)
├── SpeakerTitle (text layer)
├── Date (text layer)
├── Time (text layer)
└── SpeakerPhoto (placeholder layer)
```

## Troubleshooting

### "GIMP Error: Failed to generate banner"

**Problem**: GIMP isn't found or the batch script failed.

**Solutions**:
- Verify GIMP is installed: `gimp --version`
- Check that your template has all required layer names (case-sensitive)
- Ensure layer names are spelled exactly as documented
- Try opening your template manually in GIMP to verify it's not corrupted

### "Layer 'X' not found in template"

**Problem**: Your template is missing a required text layer.

**Solutions**:
- Open the template in GIMP
- Check that each text layer is named correctly (right-click → Edit Layer Attributes)
- Layer names are case-sensitive: use `Title1`, not `title1` or `TITLE1`

### Photo not appearing or positioned incorrectly

**Problem**: The `SpeakerPhoto` layer is missing or incorrectly sized.

**Solutions**:
- Ensure your template has a layer named exactly `SpeakerPhoto`
- The layer should be a regular layer (not a text layer)
- Size and position this layer where you want the photo
- Remember the photo will be scaled to fit, maintaining aspect ratio

### Output files already exist

**Problem**: Files with the same name exist in the output directory.

**Solutions**:
- The tool will overwrite existing files
- Rename or move previous versions if you need to keep them
- Consider organizing output files by event or date in subdirectories

### Fonts look different in the output

**Problem**: The template uses fonts not installed on your system.

**Solutions**:
- Install the required fonts system-wide
- Or edit the template to use fonts available on your system
- Check GIMP → Edit → Preferences → Folders → Fonts for installed fonts

## Examples

### Multiple Templates

Keep several templates for different event types:

```
templates/
├── workshop-modern.xcf    (Modern design for workshops)
├── seminar-classic.xcf    (Classic design for seminars)
├── webinar-simple.xcf     (Minimal design for webinars)
└── conference-bold.xcf    (Bold design for conferences)
```

The GUI will list all of them for easy selection.

### Batch Processing

While this tool focuses on single-banner generation with GUI feedback, you can run it multiple times for different events. For true batch processing from CSV, see the future roadmap in `TODO.md`.

## Project Structure

```
ai-cdmx-banner-draft-maker/
├── banner_gui.py       # Main application script
├── pyproject.toml      # Python project configuration (for uv)
├── README.md           # This file
└── TODO.md             # Future enhancements and ideas
```

## License

This is an open-source tool. Feel free to modify and distribute as needed.

## Support

For issues, suggestions, or contributions, please reach out or submit a pull request.

