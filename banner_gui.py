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


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = BannerGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

