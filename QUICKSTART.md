# Quick Start Guide

## First Time Setup

1. **Ensure GIMP is installed:**
   ```bash
   gimp --version
   ```
   If not installed: `sudo pacman -S gimp` (Arch) or `sudo apt install gimp` (Ubuntu)

2. **Run the tool:**
   ```bash
   uv run banner_gui.py
   ```
   Or without uv:
   ```bash
   python3 banner_gui.py
   ```

## Creating Your First Template

### Option 1: Manual Template Creation

1. Open GIMP and create a new image (e.g., 1920x1080 for social media)
2. Add your background design
3. Create text layers with these **exact names** (Layer → Text → Edit Layer Attributes):
   - `Title1` - Main event title
   - `Title2` - Subtitle (optional)
   - `SpeakerName` - Speaker's name
   - `SpeakerTitle` - Speaker's role (optional)
   - `Date` - Event date
   - `Time` - Event time
4. Create a placeholder for the photo:
   - Layer → New Layer
   - Name it exactly `SpeakerPhoto`
   - Position and size where you want the speaker photo
5. Save as `.xcf` in your templates directory

### Option 2: Quick Test Template

Create a simple test template to verify everything works:

1. Open GIMP
2. File → New → 1200x630 (Facebook event size)
3. Add a white background layer
4. Add 7 text layers with the required names (see above)
5. Add a 300x300 layer for `SpeakerPhoto`
6. Save as `test-template.xcf`

## Generating Your First Banner

1. Launch the tool: `uv run banner_gui.py`
2. Browse to your templates directory
3. Select your template from the list
4. Browse to your output directory (e.g., `~/output/`)
5. Fill in the fields:
   - Title 1: "AI Workshop"
   - Speaker Name: "Dr. Jane Smith"
   - Date: "December 15, 2025"
   - Time: "7:00 PM"
   - (Optional) Browse to a speaker photo
6. Click "Generate & Open in GIMP"
7. The tool will:
   - Create `2025-12-15-ai-worksho.xcf` (editable)
   - Create `2025-12-15-ai-worksho.png` (ready to share)
   - Open the XCF in GIMP for final tweaks

## Tips

- The output directory and time fields remember your last values within a session
- Date parsing is flexible: try "Dec 15, 2025", "2025-12-15", or "15/12/2025"
- The first 10 characters of Title 1 are used in the filename
- Keep templates organized in one directory for easy selection
- Export the PNG if no changes are needed; edit the XCF if you need adjustments

## Troubleshooting

**"Layer not found"**: Make sure your template layers are named exactly as documented (case-sensitive)

**GIMP not found**: Ensure GIMP is on your PATH: `which gimp`

**Photo not appearing**: Check that your template has a `SpeakerPhoto` layer

See `README.md` for full documentation and `TODO.md` for future features!

