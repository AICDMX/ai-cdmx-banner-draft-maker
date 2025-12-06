"""
GIMP Banner Generator - GUI Module

Provides the tkinter-based GUI for interactive banner generation.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import subprocess
import os
import re
import json
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from gimp_scripts_gimp3 import generate_banner_script_gimp3


class BannerGeneratorGUI:
    """Main GUI application for the GIMP banner generator"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("GIMP Banner Generator")
        self.root.geometry("600x700")
        
        # Session state for remembering values
        self.last_output_dir = ""
        self.last_time = ""
        
        # Config file path for persistent settings
        self.config_dir = Path.home() / ".config" / "gimp-banner-generator"
        self.config_file = self.config_dir / "config.json"
        
        # Load saved configuration
        self.config = self.load_config()
        
        self.setup_ui()
        self.restore_saved_settings()
        
        # Save config when window closes
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def bind_select_all(self, widget):
        """Bind Ctrl+A and click/focus events to select all text in an Entry widget"""
        def select_all(event):
            widget.select_range(0, tk.END)
            return 'break'
        widget.bind('<Control-a>', select_all)
        widget.bind('<Control-A>', select_all)  # Also handle Shift+Ctrl+A
        
        # Select all text when clicking on the field
        def on_click(event):
            widget.after_idle(lambda: widget.select_range(0, tk.END))
        widget.bind('<Button-1>', on_click)
        
        # Select all text when field gets focus
        def on_focus(event):
            widget.after_idle(lambda: widget.select_range(0, tk.END))
        widget.bind('<FocusIn>', on_focus)
    
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
        template_dir_entry = ttk.Entry(main_frame, textvariable=self.template_dir_var, width=50)
        template_dir_entry.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        self.bind_select_all(template_dir_entry)
        ttk.Button(main_frame, text="Browse", command=self.browse_template_dir).grid(
            row=row, column=2, padx=(5, 0), pady=(0, 5))
        row += 1
        
        # Template Selection
        ttk.Label(main_frame, text="Select Template:").grid(
            row=row, column=0, sticky=tk.W, pady=(5, 5))
        row += 1
        
        self.template_listbox = tk.Listbox(main_frame, height=4, width=50)
        self.template_listbox.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        self.template_listbox.bind('<<ListboxSelect>>', self.on_template_selected)
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
        output_dir_entry = ttk.Entry(main_frame, textvariable=self.output_dir_var, width=50)
        output_dir_entry.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        self.bind_select_all(output_dir_entry)
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
        self.bind_select_all(self.title1_entry)
        row += 1
        
        # Title 2
        ttk.Label(main_frame, text="Title 2:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.title2_entry = ttk.Entry(main_frame, width=50)
        self.title2_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        self.bind_select_all(self.title2_entry)
        row += 1
        
        # Speaker Name
        ttk.Label(main_frame, text="Speaker Name:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.speaker_name_entry = ttk.Entry(main_frame, width=50)
        self.speaker_name_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        self.bind_select_all(self.speaker_name_entry)
        row += 1
        
        # Speaker Title
        ttk.Label(main_frame, text="Speaker Title:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.speaker_title_entry = ttk.Entry(main_frame, width=50)
        self.speaker_title_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        self.bind_select_all(self.speaker_title_entry)
        row += 1
        
        # Date (free text)
        ttk.Label(main_frame, text="Date (e.g., Dec 31, 2025 or 2025-12-31):").grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.date_entry = ttk.Entry(main_frame, width=50)
        self.date_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        self.bind_select_all(self.date_entry)
        row += 1
        
        # Time (free text, with memory)
        ttk.Label(main_frame, text="Time:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.time_entry = ttk.Entry(main_frame, width=50)
        self.time_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        self.bind_select_all(self.time_entry)
        row += 1
        
        # Speaker Photo
        ttk.Label(main_frame, text="Speaker Photo (optional):").grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5))
        row += 1
        
        self.photo_path_var = tk.StringVar()
        photo_path_entry = ttk.Entry(main_frame, textvariable=self.photo_path_var, width=50)
        photo_path_entry.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        self.bind_select_all(photo_path_entry)
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
    
    def load_config(self) -> dict:
        """Load configuration from JSON file"""
        default_config = {
            "template_directory": "",
            "last_template": "",
            "output_directory": "",
            "title1": "",
            "title2": "",
            "speaker_name": "",
            "speaker_title": "",
            "date": "",
            "time": "",
            "photo_path": ""
        }
        
        if not self.config_file.exists():
            return default_config
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults to handle missing keys
                return {**default_config, **config}
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config file: {e}")
            return default_config
    
    def save_config(self):
        """Save current configuration to JSON file"""
        # Get current template selection
        selected_template = self.get_selected_template()
        
        config = {
            "template_directory": self.template_dir_var.get(),
            "last_template": selected_template,
            "output_directory": self.output_dir_var.get(),
            "title1": self.title1_entry.get(),
            "title2": self.title2_entry.get(),
            "speaker_name": self.speaker_name_entry.get(),
            "speaker_title": self.speaker_title_entry.get(),
            "date": self.date_entry.get(),
            "time": self.time_entry.get(),
            "photo_path": self.photo_path_var.get()
        }
        
        # Update self.config so refresh_templates() uses the latest value
        self.config.update(config)
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config file: {e}")
    
    def restore_saved_settings(self):
        """Restore settings from saved configuration"""
        # Restore template directory
        if self.config.get("template_directory"):
            self.template_dir_var.set(self.config["template_directory"])
            # refresh_templates() will restore the last_template from config
            self.refresh_templates()
        
        # Restore output directory
        if self.config.get("output_directory"):
            self.output_dir_var.set(self.config["output_directory"])
            self.last_output_dir = self.config["output_directory"]
        
        # Restore all event fields
        if self.config.get("title1"):
            self.title1_entry.insert(0, self.config["title1"])
        if self.config.get("title2"):
            self.title2_entry.insert(0, self.config["title2"])
        if self.config.get("speaker_name"):
            self.speaker_name_entry.insert(0, self.config["speaker_name"])
        if self.config.get("speaker_title"):
            self.speaker_title_entry.insert(0, self.config["speaker_title"])
        if self.config.get("date"):
            self.date_entry.insert(0, self.config["date"])
        if self.config.get("time"):
            self.time_entry.insert(0, self.config["time"])
            self.last_time = self.config["time"]
        if self.config.get("photo_path"):
            self.photo_path_var.set(self.config["photo_path"])
    
    def get_selected_template(self) -> str:
        """Get the currently selected template name"""
        selection = self.template_listbox.curselection()
        if selection:
            return self.template_listbox.get(selection[0])
        return ""
    
    def select_template_by_name(self, template_name: str):
        """Select a template in the listbox by name"""
        for i in range(self.template_listbox.size()):
            if self.template_listbox.get(i) == template_name:
                self.template_listbox.selection_clear(0, tk.END)
                self.template_listbox.selection_set(i)
                self.template_listbox.see(i)
                break
    
    def on_template_selected(self, event):
        """Handle template selection event"""
        # Save config when user selects a different template
        # This ensures the selection persists between restarts
        # Update config immediately so refresh_templates() uses the latest value
        selected_template = self.get_selected_template()
        if selected_template:
            self.config["last_template"] = selected_template
        self.save_config()
    
    def browse_template_dir(self):
        """Browse for template directory"""
        initial_dir = self.template_dir_var.get() if self.template_dir_var.get() else None
        directory = filedialog.askdirectory(
            title="Select Template Directory",
            initialdir=initial_dir
        )
        if directory:
            self.template_dir_var.set(directory)
            self.refresh_templates()
            # Save config after refreshing (refresh_templates will restore last template if it exists)
            self.save_config()
    
    def refresh_templates(self):
        """Refresh the list of available templates"""
        # Remember current selection before clearing
        current_selection = self.get_selected_template()
        
        self.template_listbox.delete(0, tk.END)
        template_dir = self.template_dir_var.get()
        
        if not template_dir or not os.path.isdir(template_dir):
            return
        
        # Find all .xcf files in the directory
        templates = sorted([f for f in os.listdir(template_dir) if f.endswith('.xcf')])
        
        for template in templates:
            self.template_listbox.insert(tk.END, template)
        
        # Try to restore the last selected template if it still exists
        # Use the saved config value, which should be up-to-date
        last_template = self.config.get("last_template", "")
        if last_template and last_template in templates:
            self.select_template_by_name(last_template)
        elif current_selection and current_selection in templates:
            # If current selection still exists, keep it
            self.select_template_by_name(current_selection)
            # Save this selection to config
            self.config["last_template"] = current_selection
    
    def browse_output_dir(self):
        """Browse for output directory"""
        initial_dir = self.output_dir_var.get() if self.output_dir_var.get() else self.last_output_dir
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=initial_dir if initial_dir else None
        )
        if directory:
            self.output_dir_var.set(directory)
            self.last_output_dir = directory
            self.save_config()
    
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
    
    def get_gimp_version(self) -> tuple:
        """
        Detect GIMP version by running gimp --version.
        Returns (major, minor) version tuple, or (2, 10) as default fallback.
        """
        try:
            gimp_binary = 'gimp-console' if shutil.which('gimp-console') else 'gimp'
            result = subprocess.run(
                [gimp_binary, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse version string like "GIMP version 3.0.6" or "GIMP 2.10.34"
                version_output = result.stdout.strip()
                import re
                match = re.search(r'(\d+)\.(\d+)', version_output)
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    return (major, minor)
        except Exception:
            pass
        # Default to 2.10 if detection fails
        return (2, 10)
    
    def build_gimp_command(self, script_file: str) -> list:
        """
        Build GIMP command for headless batch execution.
        Prefers gimp-console over gimp for batch operations as it's designed for headless use.
        Always uses xvfb-run when available to ensure a clean virtual display.
        """
        # Prefer gimp-console for batch operations (better for headless)
        gimp_binary = 'gimp-console' if shutil.which('gimp-console') else 'gimp'
        gimp_cmd = [gimp_binary, '-i', '--batch-interpreter', 'python-fu-eval', '-b', f'exec(open("{script_file}").read())', '--quit']
        
        # Always use xvfb-run for batch operations when available
        # This ensures a clean, isolated environment even if DISPLAY is set incorrectly
        if shutil.which('xvfb-run'):
            return ['xvfb-run', '-a'] + gimp_cmd
        else:
            # xvfb-run not available
            # Check if DISPLAY is set - if not, we'll get an error
            if not os.environ.get('DISPLAY'):
                # No display and no xvfb-run - this will likely fail
                # But try anyway with --no-interface flag
                gimp_cmd.insert(1, '--no-interface')
            return gimp_cmd
    
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
            
            # Save config with current template and settings
            self.save_config()
            
            # Open the XCF in GIMP for manual editing
            subprocess.Popen(['gimp', output_xcf])
            
            messagebox.showinfo(
                "Success", 
                f"Banner generated!\n\nXCF: {base_filename}.xcf\nPNG: {base_filename}.png\n\nOpening in GIMP..."
            )
            
        except subprocess.CalledProcessError:
            # Error already shown in copyable popup by update_banner, no need to show another
            pass
        except Exception as e:
            # Show generic errors in copyable popup instead of messagebox
            error_msg = f"An error occurred: {e}\n\n{type(e).__name__}: {str(e)}"
            self.root.after(100, lambda logs=error_msg: self.show_logs_popup("Error", logs))
    
    def generate_banner_script(self, template_path: str, title1: str, title2: str,
                               speaker_name: str, speaker_title: str, date: str, time: str,
                               photo_path: str, output_xcf: str, output_png: str) -> str:
        """
        Generate GIMP script for updating banner template.
        Returns script content compatible with detected GIMP version.
        """
        # Escape strings for Python script
        def escape(s):
            return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        
        # Detect GIMP version
        gimp_version = self.get_gimp_version()
        is_gimp3 = gimp_version[0] >= 3
        
        if is_gimp3:
            # GIMP 3.0+ batch scripts: use gi.repository with proper PDB procedure calls
            script = f'''
import sys
import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp, Gio

# Get PDB
pdb = Gimp.get_pdb()

# Load the template using PDB procedure properly
proc = pdb.lookup_procedure("gimp-file-load")
config = proc.create_config()
# Use Gio.File instead of Gimp.File
file_obj = Gio.File.new_for_path("{escape(template_path)}")
config.set_property("file", file_obj)
result = proc.run(config)
# Extract image from result - result is a Gimp.ValueArray
# ValueArray has length() method and can be indexed
try:
    # In GIMP 3.0, result is a Gimp.Image directly or in a ValueArray
    if hasattr(result, 'list_layers'):
        image = result
    else:
        image = result.index(0).get_image() if result else None
except (IndexError, AttributeError):
    image = None

# Build layer dictionary using GIMP 3.0 API
layers = {{}}
if image:
    for layer in image.get_layers():
        layers[layer.get_name()] = layer

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
        layer = layers[layer_name]
        # Use PDB procedure to set text
        try:
            proc = pdb.lookup_procedure("gimp-text-layer-set-text")
            if proc:
                config = proc.create_config()
                config.set_property("layer", layer)
                config.set_property("text", text_value)
                proc.run(config)
        except Exception as e:
            print(f"Warning: Could not update layer '{{layer_name}}': {{e}}")
    else:
        print("Warning: Layer '{{}}' not found in template".format(layer_name))

'''
            # Add photo handling if photo is provided
            if photo_path:
                script += f'''
# Handle speaker photo
if "SpeakerPhoto" in layers:
    try:
        photo_layer = layers["SpeakerPhoto"]

        # Load the photo as a new image using PDB procedure
        proc = pdb.lookup_procedure("gimp-file-load")
        if proc:
            config = proc.create_config()
            file_obj = Gio.File.new_for_path("{escape(photo_path)}")
            config.set_property("file", file_obj)
            photo_result = proc.run(config)
            try:
                # Extract image from result - it's at index 1 like in template loading
                photo_image = photo_result.index(1) if hasattr(photo_result, 'index') else photo_result
            except (IndexError, AttributeError):
                photo_image = None
        else:
            photo_image = None
    
    # Get active layer
    proc = pdb.lookup_procedure("gimp-image-get-active-layer")
    config = proc.create_config()
    config.set_property("image", photo_image)
    drawable_result = proc.run(config)
    try:
        photo_drawable = drawable_result.index(0).get_layer() if drawable_result else None
    except (IndexError, AttributeError):
        photo_drawable = None
    
    # Get the dimensions of the placeholder layer using GIMP 3.0 API
    placeholder_width = photo_layer.get_width()
    placeholder_height = photo_layer.get_height()
    placeholder_x, placeholder_y = photo_layer.get_offsets()
    
    # Get photo dimensions
    photo_width = photo_drawable.get_width()
    photo_height = photo_drawable.get_height()
    
    # Scale the photo to fit the placeholder (maintaining aspect ratio)
    scale_w = float(placeholder_width) / photo_width
    scale_h = float(placeholder_height) / photo_height
    scale = min(scale_w, scale_h)
    
    new_width = int(photo_width * scale)
    new_height = int(photo_height * scale)
    
    # Scale image
    proc = pdb.lookup_procedure("gimp-image-scale")
    config = proc.create_config()
    config.set_property("image", photo_image)
    config.set_property("new-width", new_width)
    config.set_property("new-height", new_height)
    proc.run(config)
    
    # Get active layer again after scaling
    proc = pdb.lookup_procedure("gimp-image-get-active-layer")
    config = proc.create_config()
    config.set_property("image", photo_image)
    drawable_result = proc.run(config)
    try:
        photo_drawable = drawable_result.index(0).get_layer() if drawable_result else None
    except (IndexError, AttributeError):
        photo_drawable = None
    
    # Copy the photo layer to the main image
    proc = pdb.lookup_procedure("gimp-layer-new-from-drawable")
    config = proc.create_config()
    config.set_property("drawable", photo_drawable)
    config.set_property("dest-image", image)
    layer_result = proc.run(config)
    try:
        new_layer = layer_result.index(0).get_layer() if layer_result else None
    except (IndexError, AttributeError):
        new_layer = None
    
    # Insert layer
    proc = pdb.lookup_procedure("gimp-image-insert-layer")
    config = proc.create_config()
    config.set_property("image", image)
    config.set_property("layer", new_layer)
    config.set_property("parent", None)
    config.set_property("position", 0)
    proc.run(config)
    
    # Position the photo at the placeholder location (centered)
    offset_x = placeholder_x + (placeholder_width - new_width) // 2
    offset_y = placeholder_y + (placeholder_height - new_height) // 2
    
    proc = pdb.lookup_procedure("gimp-layer-set-offsets")
    config = proc.create_config()
    config.set_property("layer", new_layer)
    config.set_property("x", offset_x)
    config.set_property("y", offset_y)
    proc.run(config)
    
    # Rename the new layer
    new_layer.set_name("SpeakerPhoto_Inserted")
    
    # Delete the photo image
    proc = pdb.lookup_procedure("gimp-image-delete")
    config = proc.create_config()
    config.set_property("image", photo_image)
    proc.run(config)
else:
    print("Warning: SpeakerPhoto layer not found in template")

'''
            
            # Save both XCF and PNG
            script += f'''
# Save as XCF (with layers intact) using PDB procedure
try:
    # Try gimp-xcf-save first (newer GIMP 3.0 native method)
    proc = pdb.lookup_procedure("gimp-image-save-as")
    if proc:
        config = proc.create_config()
        config.set_property("image", image)
        file_obj = Gio.File.new_for_path("{escape(output_xcf)}")
        config.set_property("file", file_obj)
        proc.run(config)
    else:
        print("Warning: Could not save XCF file")
except Exception as e:
    print(f"Warning: XCF save failed: {{e}}")

# Flatten and save as PNG
proc = pdb.lookup_procedure("gimp-image-duplicate")
config = proc.create_config()
config.set_property("image", image)
flat_result = proc.run(config)
try:
    flat_image = flat_result.index(0).get_image() if flat_result else None
except (IndexError, AttributeError):
    flat_image = None

proc = pdb.lookup_procedure("gimp-image-flatten")
config = proc.create_config()
config.set_property("image", flat_image)
proc.run(config)

proc = pdb.lookup_procedure("gimp-image-get-active-layer")
config = proc.create_config()
config.set_property("image", flat_image)
flat_result = proc.run(config)
try:
    flat_layer = flat_result.index(0).get_layer() if flat_result else None
except (IndexError, AttributeError):
    flat_layer = None

try:
    proc = pdb.lookup_procedure("file-png-save")
    if proc:
        config = proc.create_config()
        config.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
        config.set_property("image", flat_image)
        config.set_property("drawable", flat_layer)
        file_obj = Gio.File.new_for_path("{escape(output_png)}")
        config.set_property("file", file_obj)
        config.set_property("compression", 9)
        proc.run(config)
    else:
        print(f"Warning: file-png-save procedure not found, trying alternative methods")
except Exception as e:
    print(f"Warning: PNG save failed: {{e}}")

# Clean up
if flat_image:
    try:
        proc = pdb.lookup_procedure("gimp-image-delete")
        if proc:
            config = proc.create_config()
            config.set_property("image", flat_image)
            proc.run(config)
    except Exception as e:
        print(f"Warning: Could not delete flat image: {{e}}")

try:
    proc = pdb.lookup_procedure("gimp-image-delete")
    if proc:
        config = proc.create_config()
        config.set_property("image", image)
        proc.run(config)
except Exception as e:
    print(f"Warning: Could not delete image: {{e}}")

# Script completed successfully
'''
        else:
            # GIMP 2.x uses gimpfu
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
        
        return script
    
    def update_banner(self, template_path: str, title1: str, title2: str, 
                     speaker_name: str, speaker_title: str, date: str, time: str,
                     photo_path: str, output_xcf: str, output_png: str):
        """
        Use headless GIMP to update the template with provided values.
        Saves both XCF (with layers) and PNG (flattened) versions.
        """
        # Generate the script
        script = self.generate_banner_script(
            template_path, title1, title2, speaker_name, speaker_title,
            date, time, photo_path, output_xcf, output_png
        )
        
        # Write script to a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            script_file = f.name
            f.write(script)
        
        try:
            # Run GIMP in batch mode (with headless support)
            gimp_cmd = self.build_gimp_command(script_file)
            # Debug: log the command being executed
            print(f"DEBUG: Executing GIMP command: {' '.join(gimp_cmd)}")
            
            # Create a clean environment for GIMP (remove uv/virtualenv vars that might interfere)
            env = os.environ.copy()
            # Remove virtualenv-related vars that might confuse GIMP's Python
            env.pop('VIRTUAL_ENV', None)
            env.pop('VIRTUAL_ENV_PROMPT', None)
            # Keep PYTHONPATH only if it's system-wide, not venv-specific
            if 'PYTHONPATH' in env and '.venv' in env['PYTHONPATH']:
                env.pop('PYTHONPATH', None)
            
            result = subprocess.run(
                gimp_cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=60,  # 60 second timeout for banner generation
                env=env  # Use clean environment
            )
            
            # Collect logs
            logs = []
            if result.stdout:
                logs.append("=== STDOUT ===\n")
                logs.append(result.stdout)
            if result.stderr:
                logs.append("\n=== STDERR ===\n")
                logs.append(result.stderr)
            
            log_output = "".join(logs) if logs else "No output from GIMP"
            
            # Print to terminal
            print("=== GIMP Banner Generation Logs ===")
            print(log_output)
            print("=" * 40)
            
            # Show logs in popup
            self.root.after(100, lambda logs=log_output: self.show_logs_popup("Banner Generation Logs", logs))
            
        except subprocess.TimeoutExpired as e:
            error_msg = (
                f"GIMP operation timed out after 60 seconds.\n\n"
                f"This might indicate:\n"
                f"- GIMP is stuck processing a large image\n"
                f"- The template file is corrupted or very large\n"
                f"- System resources are constrained\n\n"
                f"Try:\n"
                f"- Checking if the template file is valid\n"
                f"- Reducing image sizes\n"
                f"- Checking system resources\n"
            )
            print("=== GIMP Banner Generation Timeout ===", file=sys.stderr)
            print(error_msg, file=sys.stderr)
            self.root.after(100, lambda logs=error_msg: self.show_logs_popup("Banner Generation Timeout", logs))
            raise
        except subprocess.CalledProcessError as e:
            # Collect error logs
            logs = []
            if e.stdout:
                logs.append("=== STDOUT ===\n")
                logs.append(e.stdout)
            if e.stderr:
                logs.append("\n=== STDERR ===\n")
                logs.append(e.stderr)
            
            log_output = "".join(logs) if logs else f"Error: {e}"
            
            # Check if this is a display-related error
            error_text = log_output.lower()
            if 'display' in error_text or 'gdk_display' in error_text:
                help_msg = (
                    "\n\n=== DISPLAY ERROR DETECTED ===\n"
                    "GIMP needs a display server to run. If you're running headless:\n"
                    "1. Install xvfb: sudo pacman -S xorg-server-xvfb (Arch) or sudo apt install xvfb (Ubuntu)\n"
                    "2. Or set DISPLAY environment variable if using X11 forwarding\n"
                    "3. Or run this GUI application in an environment with a display server\n"
                )
                log_output += help_msg
            
            # Print to terminal
            print("=== GIMP Banner Generation Error ===", file=sys.stderr)
            print(log_output, file=sys.stderr)
            print("=" * 40, file=sys.stderr)
            
            # Show logs in popup
            self.root.after(100, lambda logs=log_output: self.show_logs_popup("Banner Generation Error", logs))
            
            # Re-raise to be handled by caller
            raise
        finally:
            # Clean up temp file
            try:
                os.unlink(script_file)
            except:
                pass
    
    def show_logs_popup(self, title: str, logs: str):
        """Show logs in a copyable popup window"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("700x500")
        dialog.transient(self.root)
        
        # Create a frame for the text widget
        text_frame = ttk.Frame(dialog, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrolled text widget (copyable)
        log_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=('Courier', 10),
            state=tk.NORMAL,
            exportselection=True  # Allow copying selected text to clipboard
        )
        log_text.pack(fill=tk.BOTH, expand=True)
        
        # Insert logs
        log_text.insert('1.0', logs)
        
        # Configure as read-only but selectable
        # In modern tkinter, disabled widgets still allow text selection and copying
        log_text.config(state=tk.DISABLED)
        
        # Buttons frame
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X)
        
        # Copy button
        def copy_logs():
            dialog.clipboard_clear()
            dialog.clipboard_append(logs)
            messagebox.showinfo("Copied", "Logs copied to clipboard!", parent=dialog)
        
        ttk.Button(button_frame, text="Copy to Clipboard", command=copy_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def on_closing(self):
        """Handle window close event - save config before closing"""
        self.save_config()
        self.root.destroy()
    
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
        self.bind_select_all(name_entry)
        
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
        self.bind_select_all(custom_width_entry)
        
        ttk.Label(dialog, text="Custom Height:").grid(
            row=11, column=0, sticky=tk.W, padx=30, pady=(5, 10))
        custom_height_var = tk.StringVar(value="1080")
        custom_height_entry = ttk.Entry(dialog, textvariable=custom_height_var, width=15)
        custom_height_entry.grid(row=11, column=1, sticky=tk.W, padx=10, pady=(5, 10))
        self.bind_select_all(custom_height_entry)
        
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
                # Select the newly created template
                self.select_template_by_name(template_name)
                # Save config with the new template selected
                self.save_config()
                # Open in GIMP for editing
                subprocess.Popen(['gimp', template_path])
            except subprocess.CalledProcessError:
                # Error already shown in copyable popup by generate_template_file, no need to show another
                pass
            except Exception as e:
                # Show generic errors in copyable popup instead of messagebox
                error_msg = f"Failed to create template: {e}\n\n{type(e).__name__}: {str(e)}"
                self.root.after(100, lambda logs=error_msg: self.show_logs_popup("Template Creation Error", logs))
        
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
    
    def generate_template_script(self, output_path: str, width: int, height: int) -> str:
        """
        Generate GIMP script for creating a blank template.
        Returns script content compatible with detected GIMP version.
        """
        # Escape strings for Python script
        def escape(s):
            return s.replace('\\', '\\\\').replace('"', '\\"')
        
        # Detect GIMP version
        gimp_version = self.get_gimp_version()
        is_gimp3 = gimp_version[0] >= 3
        
        if is_gimp3:
            # GIMP 3.0+ uses gi.repository.Gimp
            # In batch scripts, GIMP is already initialized
            script = f'''
import sys
import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp

# Get PDB (GIMP is already initialized in batch mode)
pdb = Gimp.get_pdb()

# Create new image using PDB
image = pdb.gimp_image_new({width}, {height}, Gimp.ImageType.RGB)

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
    # Create text layer using PDB
    text_layer = pdb.gimp_text_layer_new(image, default_text, "Sans-serif", font_size, Gimp.Unit.PIXEL)
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
photo_size = min(int({width} * 0.25), int({height} * 0.4))
photo_x = {width//2} - photo_size // 2
photo_y = {height//2} - int({height} * 0.08)

photo_layer = pdb.gimp_layer_new(image, photo_size, photo_size, Gimp.ImageType.RGBA_IMAGE, "SpeakerPhoto", 50, Gimp.LayerMode.NORMAL)
pdb.gimp_image_insert_layer(image, photo_layer, None, 0)
pdb.gimp_layer_set_offsets(photo_layer, photo_x, photo_y)

# Fill photo placeholder with a semi-transparent gray rectangle
pdb.gimp_context_set_foreground((180, 180, 180))
pdb.gimp_drawable_fill(photo_layer, Gimp.FillType.FOREGROUND)

# Add a border to the photo placeholder
pdb.gimp_image_select_rectangle(image, Gimp.ChannelOps.REPLACE, photo_x, photo_y, photo_size, photo_size)
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

# Save the template using PDB
pdb.gimp_xcf_save(0, image, None, "{escape(output_path)}", "{escape(output_path)}")

# Clean up
pdb.gimp_image_delete(image)

# Script completed successfully
'''
        else:
            # GIMP 2.x uses gimpfu
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
        
        return script
    
    def generate_template_file(self, output_path: str, width: int, height: int):
        """
        Generate a blank GIMP template with properly named layers.
        Uses headless GIMP to create the template.
        """
        # Generate the script
        script = self.generate_template_script(output_path, width, height)
        
        # Write script to a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            script_file = f.name
            f.write(script)
        
        try:
            # Run GIMP in batch mode (with headless support)
            gimp_cmd = self.build_gimp_command(script_file)
            # Debug: log the command being executed
            print(f"DEBUG: Executing GIMP command: {' '.join(gimp_cmd)}")
            
            # Create a clean environment for GIMP (remove uv/virtualenv vars that might interfere)
            env = os.environ.copy()
            # Remove virtualenv-related vars that might confuse GIMP's Python
            env.pop('VIRTUAL_ENV', None)
            env.pop('VIRTUAL_ENV_PROMPT', None)
            # Keep PYTHONPATH only if it's system-wide, not venv-specific
            if 'PYTHONPATH' in env and '.venv' in env['PYTHONPATH']:
                env.pop('PYTHONPATH', None)
            
            result = subprocess.run(
                gimp_cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
                env=env  # Use clean environment
            )
            
            # Collect logs
            logs = []
            if result.stdout:
                logs.append("=== STDOUT ===\n")
                logs.append(result.stdout)
            if result.stderr:
                logs.append("\n=== STDERR ===\n")
                logs.append(result.stderr)
            
            log_output = "".join(logs) if logs else "No output from GIMP"
            
            # Print to terminal
            print("=== GIMP Template Creation Logs ===")
            print(log_output)
            print("=" * 40)
            
            # Show logs in popup
            self.root.after(100, lambda logs=log_output: self.show_logs_popup("Template Creation Logs", logs))
            
        except subprocess.CalledProcessError as e:
            # Collect error logs
            logs = []
            if e.stdout:
                logs.append("=== STDOUT ===\n")
                logs.append(e.stdout)
            if e.stderr:
                logs.append("\n=== STDERR ===\n")
                logs.append(e.stderr)
            
            log_output = "".join(logs) if logs else f"Error: {e}"
            
            # Check if this is a display-related error
            error_text = log_output.lower()
            if 'display' in error_text or 'gdk_display' in error_text:
                help_msg = (
                    "\n\n=== DISPLAY ERROR DETECTED ===\n"
                    "GIMP needs a display server to run. If you're running headless:\n"
                    "1. Install xvfb: sudo pacman -S xorg-server-xvfb (Arch) or sudo apt install xvfb (Ubuntu)\n"
                    "2. Or set DISPLAY environment variable if using X11 forwarding\n"
                    "3. Or run this GUI application in an environment with a display server\n"
                )
                log_output += help_msg
            
            # Print to terminal
            print("=== GIMP Template Creation Error ===", file=sys.stderr)
            print(log_output, file=sys.stderr)
            print("=" * 40, file=sys.stderr)
            
            # Show logs in popup
            self.root.after(100, lambda logs=log_output: self.show_logs_popup("Template Creation Error", logs))
            
            # Re-raise to be handled by caller
            raise
        except subprocess.TimeoutExpired as e:
            error_msg = f"GIMP operation timed out after 30 seconds.\n\n{e}"
            print("=== GIMP Template Creation Timeout ===", file=sys.stderr)
            print(error_msg, file=sys.stderr)
            self.root.after(100, lambda logs=error_msg: self.show_logs_popup("Template Creation Timeout", logs))
            raise
        finally:
            # Clean up temp file
            try:
                os.unlink(script_file)
            except:
                pass


