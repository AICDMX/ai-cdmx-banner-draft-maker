#!/usr/bin/env python3
"""
GIMP Banner Generator - GUI tool for generating event banners from GIMP templates
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional


class BannerGeneratorGUI:
    """Main GUI application for the GIMP banner generator"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("GIMP Banner Generator")
        self.root.geometry("600x700")
        
        # Session state for remembering values
        self.last_output_dir = ""
        self.last_time = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up all GUI components"""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        row = 0
        
        # Template Directory Section
        ttk.Label(main_frame, text="Template Directory:", font=('', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        
        self.template_dir_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.template_dir_var, width=50).grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Button(main_frame, text="Browse", command=self.browse_template_dir).grid(
            row=row, column=2, padx=(5, 0), pady=(0, 5))
        row += 1
        
        # Template Selection
        ttk.Label(main_frame, text="Select Template:").grid(
            row=row, column=0, sticky=tk.W, pady=(5, 5))
        row += 1
        
        self.template_listbox = tk.Listbox(main_frame, height=4, width=50)
        self.template_listbox.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Button(main_frame, text="Refresh", command=self.refresh_templates).grid(
            row=row, column=2, padx=(5, 0), pady=(0, 5))
        row += 1
        
        # Template Creation Button
        ttk.Button(main_frame, text="Create New Template", 
                  command=self.create_new_template,
                  style='Accent.TButton').grid(
            row=row, column=0, columnspan=3, pady=(10, 10), sticky=(tk.W, tk.E))
        row += 1
        
        # Output Directory Section
        ttk.Label(main_frame, text="Output Directory:", font=('', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5))
        row += 1
        
        self.output_dir_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_dir_var, width=50).grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Button(main_frame, text="Browse", command=self.browse_output_dir).grid(
            row=row, column=2, padx=(5, 0), pady=(0, 5))
        row += 1
        
        # Event Fields Section
        ttk.Label(main_frame, text="Event Details:", font=('', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5))
        row += 1
        
        # Title 1
        ttk.Label(main_frame, text="Title 1:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.title1_entry = ttk.Entry(main_frame, width=50)
        self.title1_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1
        
        # Title 2
        ttk.Label(main_frame, text="Title 2:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.title2_entry = ttk.Entry(main_frame, width=50)
        self.title2_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1
        
        # Speaker Name
        ttk.Label(main_frame, text="Speaker Name:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.speaker_name_entry = ttk.Entry(main_frame, width=50)
        self.speaker_name_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1
        
        # Speaker Title
        ttk.Label(main_frame, text="Speaker Title:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.speaker_title_entry = ttk.Entry(main_frame, width=50)
        self.speaker_title_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1
        
        # Date (free text)
        ttk.Label(main_frame, text="Date (e.g., Dec 31, 2025 or 2025-12-31):").grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.date_entry = ttk.Entry(main_frame, width=50)
        self.date_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1
        
        # Time (free text, with memory)
        ttk.Label(main_frame, text="Time:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.time_entry = ttk.Entry(main_frame, width=50)
        self.time_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1
        
        # Speaker Photo
        ttk.Label(main_frame, text="Speaker Photo (optional):").grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5))
        row += 1
        
        self.photo_path_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.photo_path_var, width=50).grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Button(main_frame, text="Browse", command=self.browse_photo).grid(
            row=row, column=2, padx=(5, 0), pady=(0, 5))
        row += 1
        
        # Generate Button
        ttk.Button(main_frame, text="Generate & Open in GIMP", 
                  command=self.generate_banner, 
                  style='Accent.TButton').grid(
            row=row, column=0, columnspan=3, pady=(20, 10), sticky=(tk.W, tk.E))
        
        # Configure grid weights for resizing
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def browse_template_dir(self):
        """Browse for template directory"""
        directory = filedialog.askdirectory(title="Select Template Directory")
        if directory:
            self.template_dir_var.set(directory)
            self.refresh_templates()
    
    def refresh_templates(self):
        """Refresh the list of available templates"""
        self.template_listbox.delete(0, tk.END)
        template_dir = self.template_dir_var.get()
        
        if not template_dir or not os.path.isdir(template_dir):
            return
        
        # Find all .xcf files in the directory
        templates = sorted([f for f in os.listdir(template_dir) if f.endswith('.xcf')])
        
        for template in templates:
            self.template_listbox.insert(tk.END, template)
    
    def browse_output_dir(self):
        """Browse for output directory"""
        initial_dir = self.last_output_dir if self.last_output_dir else None
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=initial_dir
        )
        if directory:
            self.output_dir_var.set(directory)
            self.last_output_dir = directory
    
    def browse_photo(self):
        """Browse for speaker photo"""
        path = filedialog.askopenfilename(
            title="Select Speaker Photo",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        if path:
            self.photo_path_var.set(path)
    
    def parse_date_from_text(self, date_text: str) -> Optional[str]:
        """
        Try to extract a date from free-form text and return YYYY-MM-DD format.
        Tries multiple common patterns.
        """
        if not date_text:
            return None
        
        # Pattern 1: YYYY-MM-DD (anywhere in text)
        match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_text)
        if match:
            year, month, day = match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Pattern 2: MM/DD/YYYY or DD/MM/YYYY
        match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_text)
        if match:
            # Assume MM/DD/YYYY for US format
            part1, part2, year = match.groups()
            month, day = part1, part2
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Pattern 3: Month name formats (Dec 31, 2025 or December 31, 2025)
        month_names = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'june': '06', 'july': '07', 'august': '08', 'september': '09',
            'october': '10', 'november': '11', 'december': '12'
        }
        
        for month_name, month_num in month_names.items():
            # Pattern: "Dec 31, 2025" or "December 31, 2025"
            pattern = rf'\b{month_name}\.?\s+(\d{{1,2}}),?\s+(\d{{4}})\b'
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                day, year = match.groups()
                return f"{year}-{month_num}-{day.zfill(2)}"
            
            # Pattern: "31 Dec 2025" or "31 December 2025"
            pattern = rf'\b(\d{{1,2}})\s+{month_name}\.?\s+(\d{{4}})\b'
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                day, year = match.groups()
                return f"{year}-{month_num}-{day.zfill(2)}"
        
        return None
    
    def slugify(self, text: str, max_length: int = 10) -> str:
        """Convert text to a safe filename slug"""
        # Take first max_length characters
        text = text[:max_length]
        # Convert to lowercase and replace spaces/special chars with dash
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        # Remove leading/trailing dashes
        text = text.strip('-')
        return text or 'banner'
    
    def generate_banner(self):
        """Main function to generate the banner"""
        # Remember the time value for next use
        time_value = self.time_entry.get()
        if time_value:
            self.last_time = time_value
        
        # Validate required fields
        if not self.template_dir_var.get():
            messagebox.showerror("Error", "Please select a template directory")
            return
        
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a template")
            return
        
        template_name = self.template_listbox.get(selection[0])
        template_path = os.path.join(self.template_dir_var.get(), template_name)
        
        if not os.path.exists(template_path):
            messagebox.showerror("Error", f"Template file not found: {template_path}")
            return
        
        if not self.output_dir_var.get():
            messagebox.showerror("Error", "Please select an output directory")
            return
        
        if not self.title1_entry.get():
            messagebox.showerror("Error", "Title 1 is required")
            return
        
        if not self.speaker_name_entry.get():
            messagebox.showerror("Error", "Speaker Name is required")
            return
        
        if not self.date_entry.get():
            messagebox.showerror("Error", "Date is required")
            return
        
        if not self.time_entry.get():
            messagebox.showerror("Error", "Time is required")
            return
        
        # Validate speaker photo if provided
        photo_path = self.photo_path_var.get()
        if photo_path and not os.path.exists(photo_path):
            messagebox.showerror("Error", f"Speaker photo not found: {photo_path}")
            return
        
        # Build output filename
        date_text = self.date_entry.get()
        parsed_date = self.parse_date_from_text(date_text)
        
        title_slug = self.slugify(self.title1_entry.get(), 10)
        
        if parsed_date:
            base_filename = f"{parsed_date}-{title_slug}"
        else:
            base_filename = f"banner-{title_slug}"
        
        output_xcf = os.path.join(self.output_dir_var.get(), f"{base_filename}.xcf")
        output_png = os.path.join(self.output_dir_var.get(), f"{base_filename}.png")
        
        # Generate the banner using headless GIMP
        try:
            self.update_banner(
                template_path=template_path,
                title1=self.title1_entry.get(),
                title2=self.title2_entry.get(),
                speaker_name=self.speaker_name_entry.get(),
                speaker_title=self.speaker_title_entry.get(),
                date=date_text,
                time=self.time_entry.get(),
                photo_path=photo_path,
                output_xcf=output_xcf,
                output_png=output_png
            )
            
            # Open the XCF in GIMP for manual editing
            subprocess.Popen(['gimp', output_xcf])
            
            messagebox.showinfo(
                "Success", 
                f"Banner generated!\n\nXCF: {base_filename}.xcf\nPNG: {base_filename}.png\n\nOpening in GIMP..."
            )
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror(
                "GIMP Error", 
                f"Failed to generate banner.\n\nMake sure GIMP is installed and the template has the required layers:\n"
                f"Title1, Title2, SpeakerName, SpeakerTitle, Date, Time, SpeakerPhoto\n\nError: {e}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def update_banner(self, template_path: str, title1: str, title2: str, 
                     speaker_name: str, speaker_title: str, date: str, time: str,
                     photo_path: str, output_xcf: str, output_png: str):
        """
        Use headless GIMP to update the template with provided values.
        Saves both XCF (with layers) and PNG (flattened) versions.
        """
        # Escape strings for Python script
        def escape(s):
            return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        
        # Build the Python-Fu script
        script = f'''
import sys
from gimpfu import *

# Load the template
image = pdb.gimp_file_load("{escape(template_path)}", "{escape(template_path)}")

# Build layer dictionary
layers = {{}}
for layer in image.layers:
    layers[layer.name] = layer

# Update text layers
text_fields = {{
    "Title1": "{escape(title1)}",
    "Title2": "{escape(title2)}",
    "SpeakerName": "{escape(speaker_name)}",
    "SpeakerTitle": "{escape(speaker_title)}",
    "Date": "{escape(date)}",
    "Time": "{escape(time)}"
}}

for layer_name, text_value in text_fields.items():
    if layer_name in layers:
        pdb.gimp_text_layer_set_text(layers[layer_name], text_value)
    else:
        pdb.gimp_message("Warning: Layer '{{}}' not found in template".format(layer_name))

'''
        
        # Add photo handling if photo is provided
        if photo_path:
            script += f'''
# Handle speaker photo
if "SpeakerPhoto" in layers:
    photo_layer = layers["SpeakerPhoto"]
    
    # Load the photo as a new image
    photo_image = pdb.gimp_file_load("{escape(photo_path)}", "{escape(photo_path)}")
    photo_drawable = pdb.gimp_image_get_active_layer(photo_image)
    
    # Get the dimensions of the placeholder layer
    placeholder_width = photo_layer.width
    placeholder_height = photo_layer.height
    placeholder_x = photo_layer.offsets[0]
    placeholder_y = photo_layer.offsets[1]
    
    # Scale the photo to fit the placeholder (maintaining aspect ratio)
    photo_width = photo_drawable.width
    photo_height = photo_drawable.height
    
    scale_w = float(placeholder_width) / photo_width
    scale_h = float(placeholder_height) / photo_height
    scale = min(scale_w, scale_h)
    
    new_width = int(photo_width * scale)
    new_height = int(photo_height * scale)
    
    pdb.gimp_image_scale(photo_image, new_width, new_height)
    photo_drawable = pdb.gimp_image_get_active_layer(photo_image)
    
    # Copy the photo layer to the main image
    new_layer = pdb.gimp_layer_new_from_drawable(photo_drawable, image)
    pdb.gimp_image_insert_layer(image, new_layer, None, 0)
    
    # Position the photo at the placeholder location (centered)
    offset_x = placeholder_x + (placeholder_width - new_width) // 2
    offset_y = placeholder_y + (placeholder_height - new_height) // 2
    pdb.gimp_layer_set_offsets(new_layer, offset_x, offset_y)
    
    # Rename the new layer
    pdb.gimp_item_set_name(new_layer, "SpeakerPhoto_Inserted")
    
    # Delete the photo image
    pdb.gimp_image_delete(photo_image)
else:
    pdb.gimp_message("Warning: SpeakerPhoto layer not found in template")

'''
        
        # Save both XCF and PNG
        script += f'''
# Save as XCF (with layers intact)
pdb.gimp_xcf_save(0, image, None, "{escape(output_xcf)}", "{escape(output_xcf)}")

# Flatten and save as PNG
flat_image = pdb.gimp_image_duplicate(image)
pdb.gimp_image_flatten(flat_image)
flat_layer = pdb.gimp_image_get_active_layer(flat_image)
pdb.file_png_save(flat_image, flat_layer, "{escape(output_png)}", "{escape(output_png)}", 0, 9, 0, 0, 0, 0, 0)

# Clean up
pdb.gimp_image_delete(flat_image)
pdb.gimp_image_delete(image)

pdb.gimp_quit(0)
'''
        
        # Write script to a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            script_file = f.name
            f.write(script)
        
        try:
            # Run GIMP in batch mode
            result = subprocess.run(
                ['gimp', '-i', '--batch-interpreter', 'python-fu-eval', '-b', f'exec(open("{script_file}").read())'],
                capture_output=True,
                text=True,
                check=True
            )
        finally:
            # Clean up temp file
            try:
                os.unlink(script_file)
            except:
                pass
    
    def set_remembered_values(self):
        """Set remembered values from last session"""
        if self.last_output_dir:
            self.output_dir_var.set(self.last_output_dir)
        if self.last_time:
            self.time_entry.insert(0, self.last_time)
    
    def create_new_template(self):
        """Create a new blank template with properly named layers"""
        # Check if template directory is set
        template_dir = self.template_dir_var.get()
        if not template_dir:
            messagebox.showerror("Error", "Please select a template directory first")
            return
        
        if not os.path.isdir(template_dir):
            messagebox.showerror("Error", f"Template directory does not exist: {template_dir}")
            return
        
        # Create a dialog for template creation
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Template")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Template name
        ttk.Label(dialog, text="Template Name:", font=('', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=(10, 5))
        
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=40)
        name_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=(0, 10))
        
        # Dimension presets
        ttk.Label(dialog, text="Choose Dimensions:", font=('', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, padx=10, pady=(10, 5))
        
        dimension_var = tk.StringVar(value="1920x1080")
        
        presets = [
            ("1920x1080", "1920x1080 (Full HD - Facebook Event, YouTube Thumbnail)"),
            ("1200x628", "1200x628 (Facebook/LinkedIn Post)"),
            ("1080x1080", "1080x1080 (Instagram Square)"),
            ("1080x1920", "1080x1920 (Instagram Story/Reel)"),
            ("1200x675", "1200x675 (Twitter/X Post)"),
            ("1280x720", "1280x720 (HD - Web Banner)"),
            ("custom", "Custom Dimensions")
        ]
        
        for i, (value, label) in enumerate(presets):
            ttk.Radiobutton(dialog, text=label, variable=dimension_var, 
                           value=value).grid(row=3+i, column=0, sticky=tk.W, padx=20, pady=2)
        
        # Custom dimension fields
        ttk.Label(dialog, text="Custom Width:").grid(
            row=10, column=0, sticky=tk.W, padx=30, pady=(5, 0))
        custom_width_var = tk.StringVar(value="1920")
        custom_width_entry = ttk.Entry(dialog, textvariable=custom_width_var, width=15)
        custom_width_entry.grid(row=10, column=1, sticky=tk.W, padx=10, pady=(5, 0))
        
        ttk.Label(dialog, text="Custom Height:").grid(
            row=11, column=0, sticky=tk.W, padx=30, pady=(5, 10))
        custom_height_var = tk.StringVar(value="1080")
        custom_height_entry = ttk.Entry(dialog, textvariable=custom_height_var, width=15)
        custom_height_entry.grid(row=11, column=1, sticky=tk.W, padx=10, pady=(5, 10))
        
        def on_create():
            """Handle template creation"""
            template_name = name_var.get().strip()
            if not template_name:
                messagebox.showerror("Error", "Please enter a template name", parent=dialog)
                return
            
            # Add .xcf extension if not present
            if not template_name.endswith('.xcf'):
                template_name += '.xcf'
            
            # Get dimensions
            dimension_choice = dimension_var.get()
            if dimension_choice == "custom":
                try:
                    width = int(custom_width_var.get())
                    height = int(custom_height_var.get())
                    if width <= 0 or height <= 0:
                        raise ValueError("Dimensions must be positive")
                except ValueError as e:
                    messagebox.showerror("Error", f"Invalid custom dimensions: {e}", parent=dialog)
                    return
            else:
                width, height = map(int, dimension_choice.split('x'))
            
            # Full path to template
            template_path = os.path.join(template_dir, template_name)
            
            # Check if file already exists
            if os.path.exists(template_path):
                if not messagebox.askyesno("File Exists", 
                                          f"Template '{template_name}' already exists. Overwrite?",
                                          parent=dialog):
                    return
            
            try:
                self.generate_template_file(template_path, width, height)
                dialog.destroy()
                messagebox.showinfo(
                    "Success", 
                    f"Template '{template_name}' created successfully!\n\n"
                    f"Dimensions: {width}x{height}\n"
                    f"Location: {template_path}\n\n"
                    f"Opening in GIMP for customization..."
                )
                # Refresh template list
                self.refresh_templates()
                # Open in GIMP for editing
                subprocess.Popen(['gimp', template_path])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create template: {e}", parent=dialog)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=12, column=0, columnspan=2, pady=(20, 10))
        
        ttk.Button(button_frame, text="Create Template", command=on_create).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        dialog.columnconfigure(0, weight=1)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def generate_template_file(self, output_path: str, width: int, height: int):
        """
        Generate a blank GIMP template with properly named layers.
        Uses headless GIMP to create the template.
        """
        # Escape strings for Python script
        def escape(s):
            return s.replace('\\', '\\\\').replace('"', '\\"')
        
        # Build the Python-Fu script to create template
        script = f'''
import sys
from gimpfu import *

# Create new image
image = pdb.gimp_image_new({width}, {height}, RGB)

# Create background layer with a pleasant gradient
bg_layer = pdb.gimp_layer_new(image, {width}, {height}, RGB_IMAGE, "Background", 100, LAYER_MODE_NORMAL)
pdb.gimp_image_insert_layer(image, bg_layer, None, 0)

# Fill background with a gradient (white to light blue)
pdb.gimp_context_set_foreground((255, 255, 255))
pdb.gimp_context_set_background((230, 240, 255))
pdb.gimp_drawable_edit_gradient_fill(
    bg_layer,
    GRADIENT_LINEAR,
    0,
    False,
    1,
    0,
    True,
    0, 0,
    {width}, {height}
)

# Text layer specifications with positions
# Format: (name, default_text, x, y, font_size)
text_specs = [
    ("Title1", "Main Event Title", {width//2}, {height//4}, {int(width * 0.04)}),
    ("Title2", "Subtitle or Secondary Info", {width//2}, {height//4 + int(height * 0.08)}, {int(width * 0.025)}),
    ("SpeakerName", "Speaker Name", {width//2}, {height//2 + int(height * 0.15)}, {int(width * 0.035)}),
    ("SpeakerTitle", "Speaker Title or Affiliation", {width//2}, {height//2 + int(height * 0.22)}, {int(width * 0.02)}),
    ("Date", "December 31, 2025", {width - int(width * 0.15)}, {height - int(height * 0.12)}, {int(width * 0.025)}),
    ("Time", "7:00 PM MST", {width - int(width * 0.15)}, {height - int(height * 0.06)}, {int(width * 0.02)})
]

# Create text layers
for layer_name, default_text, x, y, font_size in text_specs:
    # Create text layer
    text_layer = pdb.gimp_text_layer_new(image, default_text, "Sans-serif", font_size, PIXELS)
    pdb.gimp_image_insert_layer(image, text_layer, None, 0)
    
    # Set layer name
    pdb.gimp_item_set_name(text_layer, layer_name)
    
    # Center text horizontally (for Title1, Title2, SpeakerName, SpeakerTitle)
    if layer_name in ["Title1", "Title2", "SpeakerName", "SpeakerTitle"]:
        text_width = pdb.gimp_drawable_width(text_layer)
        x_centered = x - text_width // 2
        pdb.gimp_layer_set_offsets(text_layer, x_centered, y)
    else:
        # Right-align for Date and Time
        text_width = pdb.gimp_drawable_width(text_layer)
        x_right = x - text_width
        pdb.gimp_layer_set_offsets(text_layer, x_right, y)
    
    # Set text color to dark blue for better visibility
    pdb.gimp_text_layer_set_color(text_layer, (30, 60, 120))

# Create SpeakerPhoto placeholder layer (a rectangle to show where photo goes)
photo_size = min(int(width * 0.25), int(height * 0.4))
photo_x = {width//2 - photo_size//2}
photo_y = {height//2 - int(height * 0.08)}

photo_layer = pdb.gimp_layer_new(image, photo_size, photo_size, RGBA_IMAGE, "SpeakerPhoto", 50, LAYER_MODE_NORMAL)
pdb.gimp_image_insert_layer(image, photo_layer, None, 0)
pdb.gimp_layer_set_offsets(photo_layer, photo_x, photo_y)

# Fill photo placeholder with a semi-transparent gray rectangle
pdb.gimp_context_set_foreground((180, 180, 180))
pdb.gimp_drawable_fill(photo_layer, FILL_FOREGROUND)

# Add a border to the photo placeholder
pdb.gimp_image_select_rectangle(image, CHANNEL_OP_REPLACE, photo_x, photo_y, photo_size, photo_size)
pdb.gimp_context_set_foreground((100, 100, 100))
pdb.gimp_edit_stroke(photo_layer, 3)
pdb.gimp_selection_none(image)

# Add guides for better alignment
# Horizontal center
pdb.gimp_image_add_hguide(image, {height//2})
# Vertical center
pdb.gimp_image_add_vguide(image, {width//2})
# Top third
pdb.gimp_image_add_hguide(image, {height//3})
# Bottom third
pdb.gimp_image_add_hguide(image, {2*height//3})

# Save the template
pdb.gimp_xcf_save(0, image, None, "{escape(output_path)}", "{escape(output_path)}")

# Clean up
pdb.gimp_image_delete(image)

pdb.gimp_quit(0)
'''
        
        # Write script to a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            script_file = f.name
            f.write(script)
        
        try:
            # Run GIMP in batch mode
            result = subprocess.run(
                ['gimp', '-i', '--batch-interpreter', 'python-fu-eval', '-b', f'exec(open("{script_file}").read())'],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
        finally:
            # Clean up temp file
            try:
                os.unlink(script_file)
            except:
                pass


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = BannerGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

