# GIMP Template Requirements Checklist

Use this checklist when creating or validating templates for the GIMP Banner Generator.

## Required Text Layers (Case-Sensitive)

Your template **must** include these text layers with exact names:

- [ ] `Title1` - Main event title (required)
- [ ] `Title2` - Subtitle or secondary information (optional but recommended)
- [ ] `SpeakerName` - Speaker's full name (required)
- [ ] `SpeakerTitle` - Speaker's role, title, or affiliation (optional but recommended)
- [ ] `Date` - Event date (required)
- [ ] `Time` - Event time (required)

## Speaker Photo Placeholder

- [ ] `SpeakerPhoto` - Layer for photo placement (highly recommended)
  - Should be a regular layer (not text)
  - Position and size it where you want the photo to appear
  - The tool will scale photos to fit this area while maintaining aspect ratio

## Template Design Checklist

### File Format
- [ ] Saved as `.xcf` (GIMP's native format)
- [ ] Located in your templates directory
- [ ] Named descriptively (e.g., `workshop-modern.xcf`, `seminar-classic.xcf`)

### Layer Organization
- [ ] All layers have descriptive names
- [ ] Required layers are spelled correctly (case-sensitive!)
- [ ] Text layers use readable fonts
- [ ] Background layer is at the bottom of the stack

### Text Layer Properties
- [ ] Font size is readable (recommended: 48-72pt for titles, 24-36pt for body)
- [ ] Text color contrasts well with background
- [ ] Text alignment is consistent (left, center, or right)
- [ ] Line spacing and letter spacing are appropriate
- [ ] Text layers are positioned where you want them in the final banner

### Photo Placeholder Properties
- [ ] `SpeakerPhoto` layer is positioned appropriately
- [ ] Size is adequate for headshots (recommended: 250x250 to 400x400 pixels)
- [ ] Position allows for both portrait and landscape photos
- [ ] Doesn't overlap important text or design elements

### Design Quality
- [ ] Canvas size is appropriate for your use case:
  - Social media (Facebook Event): 1920x1080 or 1200x630
  - Social media (Instagram): 1080x1080
  - Web banner: 1920x1080
  - Print: Higher resolution (e.g., 3000x2000 at 300 DPI)
- [ ] Background is complete and looks professional
- [ ] All design elements are high quality (no pixelation)
- [ ] Color scheme is consistent and matches your branding

## Testing Your Template

Before using a template in production:

1. [ ] Open the template in GIMP manually to verify it looks correct
2. [ ] Check that all layer names are spelled exactly as documented
3. [ ] Generate a test banner with sample data
4. [ ] Verify all text appears in the correct positions
5. [ ] Check that the speaker photo is properly positioned and scaled
6. [ ] Export the PNG and verify it looks good at full size
7. [ ] Test the XCF file opens correctly in GIMP for editing

## Common Mistakes to Avoid

- ❌ Using lowercase layer names (e.g., `title1` instead of `Title1`)
- ❌ Adding spaces to layer names (e.g., `Title 1` instead of `Title1`)
- ❌ Forgetting to name layers (leaving them as "Text Layer")
- ❌ Making the `SpeakerPhoto` placeholder too small
- ❌ Using fonts that aren't installed on your system
- ❌ Forgetting to include a background layer
- ❌ Making text layers too small to read
- ❌ Using low-resolution images in the background

## Quick Validation

To quickly check if your template is valid:

1. Open the template in GIMP
2. Open the Layers dialog (Windows → Dockable Dialogs → Layers)
3. Verify each required layer exists with the exact name
4. For text layers, make sure they're actually text layers (not rasterized)
5. For `SpeakerPhoto`, make sure it's a regular layer that can hold content

## Example Templates

### Minimal Template
A basic template for testing:
- Canvas: 1200x630
- Background: Solid color or simple gradient
- All 7 required layers (Title1, Title2, SpeakerName, SpeakerTitle, Date, Time, SpeakerPhoto)
- Simple fonts (Arial, Helvetica, or system default)

### Professional Template
A production-ready template:
- Canvas: 1920x1080
- Background: Branded design with logo and colors
- All 7 required layers with custom fonts
- Photo placeholder with circular mask or frame
- Additional decorative elements (borders, patterns, etc.)

## Template Naming Convention

Use descriptive names for your templates:
- `workshop-modern.xcf` - Modern design for workshops
- `seminar-classic.xcf` - Classic design for seminars  
- `webinar-minimal.xcf` - Minimal design for webinars
- `conference-bold.xcf` - Bold design for conferences

This makes it easy to select the right template from the GUI.

---

**Questions?** See `README.md` for detailed documentation or `QUICKSTART.md` for getting started.

