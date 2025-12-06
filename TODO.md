# Future Enhancements & TODO

This document tracks planned improvements and features for the GIMP Banner Generator.

## Priority Enhancements

### 1. Auto-cropping and Background Removal for Photos
- **Goal**: Automatically crop speaker photos to focus on faces and remove backgrounds
- **Implementation ideas**:
  - Integrate with `rembg` library for background removal
  - Use `opencv-python` for face detection and smart cropping
  - Add toggle in GUI: "Auto-process photo" checkbox
  - Provide preview before applying
- **Benefits**: Cleaner, more professional-looking speaker photos without manual editing

### 2. Standalone Executable (.exe)
- **Goal**: Package the tool as a standalone executable for non-technical users
- **Implementation ideas**:
  - Use PyInstaller or cx_Freeze to create executable
  - Bundle Python runtime and dependencies
  - Create installers for Windows, macOS, and Linux
  - Include a launcher that checks for GIMP installation
- **Benefits**: Users don't need Python installed; just download and run

### 3. Template Generator Function ✅ COMPLETED
- **Goal**: Create a tool to generate blank templates with properly named layers
- **Implementation**:
  - ✅ Added "Create New Template" button in GUI
  - ✅ Created dialog with template dimension presets:
    - 1920x1080 (Full HD - Facebook Event, YouTube Thumbnail)
    - 1200x628 (Facebook/LinkedIn Post)
    - 1080x1080 (Instagram Square)
    - 1080x1920 (Instagram Story/Reel)
    - 1200x675 (Twitter/X Post)
    - 1280x720 (HD - Web Banner)
    - Custom dimensions (user-defined width/height)
  - ✅ Automatically creates GIMP XCF file with all required layers:
    - Title1, Title2, SpeakerName, SpeakerTitle, Date, Time (text layers with sample text)
    - SpeakerPhoto (placeholder rectangle layer with visible border)
  - ✅ Added sample text for each layer showing what content goes where
  - ✅ Added GIMP guides (horizontal/vertical center, thirds) for better positioning
  - ✅ Creates pleasant gradient background (white to light blue)
  - ✅ Automatically positions text layers appropriately (centered titles, right-aligned date/time)
  - ✅ Saves to templates directory with user-provided name
  - ✅ Opens the new template in GIMP immediately for customization
  - ✅ Refreshes template list after creation
- **Benefits**: Makes it easy to start designing new templates without manual layer setup
- **Usage**: Click "Create New Template" button, choose dimensions, enter a name, and the template is automatically generated and opened in GIMP for customization

## Secondary Enhancements

### 4. Batch Processing from CSV
- **Goal**: Generate multiple banners from a CSV file in one go
- **Implementation**:
  - Add "Batch from CSV" button
  - CSV format: `title1,title2,speaker_name,speaker_title,date,time,photo_path,template_name`
  - Loop through rows and generate banners automatically
  - Show progress bar during batch generation
- **Benefits**: Efficient for recurring event series or conferences with many speakers

### 5. Live Preview
- **Goal**: Show a preview of the banner before generating
- **Implementation**:
  - Render a low-res preview using PIL/Pillow
  - Display in a preview panel in the GUI
  - Update preview when fields change
- **Challenges**: Would need to parse GIMP files or use GIMP's batch mode for previews
- **Benefits**: Catch mistakes before opening GIMP

### 6. Template Validation Tool
- **Goal**: Check templates for missing or incorrectly named layers
- **Implementation**:
  - Add "Validate Template" button
  - Run headless GIMP script to list all layers
  - Show which required layers are present/missing
  - Highlight issues with color coding (red = missing, green = ok)
- **Benefits**: Easier template debugging

### 7. Recent Values Persistence
- **Goal**: Remember field values across sessions (not just within one session)
- **Implementation**:
  - Save last-used values to a JSON config file (`~/.config/gimp-banner-generator/config.json`)
  - Load on startup and restore fields
  - Include template directory, output directory, and last-used time
- **Benefits**: Faster workflow for repeated use with similar events

### 8. Custom Field Mapping
- **Goal**: Allow users to define their own layer names (not limited to Title1, Title2, etc.)
- **Implementation**:
  - Add "Field Mapping" dialog
  - Let users specify which GUI field maps to which template layer name
  - Save mappings per template
- **Benefits**: Work with existing templates that use different naming conventions

### 9. Multi-language Support
- **Goal**: Support templates and GUI in multiple languages
- **Implementation**:
  - Add language selector in GUI
  - Translate labels and messages
  - Support Unicode text in all fields
- **Benefits**: Useful for international teams

### 10. Undo Last Generation
- **Goal**: Quickly delete or revert the last generated files
- **Implementation**:
  - Keep track of last output paths
  - Add "Undo Last" button that deletes the files
  - Show confirmation dialog
- **Benefits**: Clean up mistakes without browsing file system

## Technical Improvements

### 11. Better Date Parsing
- **Goal**: Support even more date formats and provide feedback
- **Implementation**:
  - Use `dateutil.parser` for robust date parsing
  - Show parsed date in GUI after typing (e.g., "Detected: 2025-12-31")
  - Allow manual override if parsing is wrong
- **Benefits**: Fewer filename issues

### 12. Error Logging
- **Goal**: Save detailed error logs for troubleshooting
- **Implementation**:
  - Log all GIMP output to `~/.local/share/gimp-banner-generator/logs/`
  - Include timestamps and full stack traces
  - Add "View Logs" button in GUI
- **Benefits**: Easier debugging for users and developers

### 13. Unit Tests
- **Goal**: Ensure reliability with automated tests
- **Implementation**:
  - Add pytest tests for date parsing, slugification, filename generation
  - Mock GIMP calls for integration tests
  - Set up CI/CD for automatic testing
- **Benefits**: Catch regressions early

### 14. Dark Mode
- **Goal**: Add a dark theme for the GUI
- **Implementation**:
  - Use `ttkthemes` for modern themes
  - Add theme selector in GUI
  - Save preference to config file
- **Benefits**: Better user experience for dark mode users

## Long-term Ideas

### 15. Web-based Version
- **Goal**: Run the tool in a browser without installing anything
- **Implementation**:
  - Build a Flask/FastAPI backend with GIMP on server
  - Create a React/Vue frontend
  - Handle file uploads for photos and templates
  - Stream generated files back to user
- **Benefits**: Accessible from any device, no installation

### 16. Cloud Template Library
- **Goal**: Share and download templates from a community library
- **Implementation**:
  - Host templates on a public repo or website
  - Add "Download Templates" button in GUI
  - Let users upload their templates to share
- **Benefits**: Kickstart users with professional designs

### 17. AI-powered Text Suggestions
- **Goal**: Suggest speaker titles or event descriptions using AI
- **Implementation**:
  - Integrate with OpenAI or local LLM
  - "Suggest Description" button that generates text based on speaker name
- **Benefits**: Save time writing descriptions

### 18. Social Media Integration
- **Goal**: Directly post generated banners to social media
- **Implementation**:
  - Add "Share to Twitter/LinkedIn" buttons
  - Use platform APIs to upload and post
  - Include event details in post text
- **Benefits**: Streamline event promotion workflow

---

## How to Contribute

If you'd like to work on any of these features:
1. Fork the repository
2. Create a feature branch
3. Implement the enhancement
4. Submit a pull request with tests and documentation

Feel free to suggest new ideas by opening an issue!

