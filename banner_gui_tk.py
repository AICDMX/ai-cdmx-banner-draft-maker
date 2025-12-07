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

from gimp_scripts_gimp3 import (
    generate_banner_script_gimp3,
    load_gimp_template,
    get_gimp_version,
    build_gimp_command
)


class BannerGeneratorGUI:
    """Main GUI application for the GIMP banner generator"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("GIMP Banner Generator")
        self.root.geometry("600x850")

        # Session state for remembering values
        self.last_output_dir = ""
        self.last_time = ""

        # Flag to prevent auto-saving during initialization
        self.initializing = True

        # Config file path for persistent settings
        self.config_dir = Path.home() / ".config" / "gimp-banner-generator"
        self.config_file = self.config_dir / "config.json"

        # Load saved configuration
        self.config = self.load_config()

        self.setup_ui()
        self.restore_saved_settings()

        # Done initializing - now auto-save is enabled
        self.initializing = False

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
        # Create a canvas with scrollbar for the entire window
        canvas = tk.Canvas(self.root, bg=self.root.cget('bg'), highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mousewheel scrolling (cross-platform)
        def _on_mousewheel(event):
            if event.num == 4:  # Linux scroll up
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # Linux scroll down
                canvas.yview_scroll(1, "units")
            else:  # Windows/macOS
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows/macOS
        canvas.bind_all("<Button-4>", _on_mousewheel)   # Linux scroll up
        canvas.bind_all("<Button-5>", _on_mousewheel)   # Linux scroll down

        # Grid canvas and scrollbar
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Configure root grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Content frame inside the scrollable area
        content_frame = ttk.Frame(scrollable_frame, padding="10")
        content_frame.pack(side="top", fill="x", expand=False)
        content_frame.columnconfigure(0, weight=1)

        main_frame = content_frame

        # Status display at the top
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var,
                                      foreground="green", font=('', 9))
        self.status_label.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        row = 1
        
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
        ttk.Label(main_frame, text="Select Template(s):", font=('', 10)).grid(
            row=row, column=0, sticky=tk.W, pady=(5, 5))
        ttk.Label(main_frame, text="(Use Ctrl+click to select multiple)", font=('', 8, 'italic')).grid(
            row=row, column=1, columnspan=2, sticky=tk.E, pady=(5, 5))
        row += 1

        self.template_listbox = tk.Listbox(main_frame, height=4, width=50, selectmode=tk.EXTENDED)
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
        self.title1_entry.bind('<FocusOut>', lambda e: not self.initializing and self.save_config())
        row += 1

        # Title 2
        ttk.Label(main_frame, text="Title 2:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.title2_entry = ttk.Entry(main_frame, width=50)
        self.title2_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        self.bind_select_all(self.title2_entry)
        self.title2_entry.bind('<FocusOut>', lambda e: not self.initializing and self.save_config())
        row += 1

        # Speaker Name
        ttk.Label(main_frame, text="Speaker Name:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.speaker_name_entry = ttk.Entry(main_frame, width=50)
        self.speaker_name_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        self.bind_select_all(self.speaker_name_entry)
        self.speaker_name_entry.bind('<FocusOut>', lambda e: not self.initializing and self.save_config())
        row += 1

        # Speaker Title
        ttk.Label(main_frame, text="Speaker Title:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.speaker_title_entry = ttk.Entry(main_frame, width=50)
        self.speaker_title_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        self.bind_select_all(self.speaker_title_entry)
        self.speaker_title_entry.bind('<FocusOut>', lambda e: not self.initializing and self.save_config())
        row += 1

        # Date (free text)
        ttk.Label(main_frame, text="Date (e.g., Dec 31, 2025 or 2025-12-31):").grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.date_entry = ttk.Entry(main_frame, width=50)
        self.date_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        self.bind_select_all(self.date_entry)
        self.date_entry.bind('<FocusOut>', lambda e: not self.initializing and self.save_config())
        row += 1

        # Time (free text, with memory)
        ttk.Label(main_frame, text="Time:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        self.time_entry = ttk.Entry(main_frame, width=50)
        self.time_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        self.bind_select_all(self.time_entry)
        self.time_entry.bind('<FocusOut>', lambda e: not self.initializing and self.save_config())
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

        # Status/messages area at the bottom - fills remaining space
        row += 1
        ttk.Label(main_frame, text="Log:", font=('', 9, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5))
        row += 1

        self.message_text = scrolledtext.ScrolledText(main_frame, height=4, width=50, state=tk.DISABLED)
        self.message_text.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        main_frame.rowconfigure(row, weight=1)

        # Configure grid weights for resizing
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
    
    def load_config(self) -> dict:
        """Load configuration from JSON file"""
        default_config = {
            "template_directory": "",
            "last_template": "",
            "last_templates": [],
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
        # Get current template selections
        selected_templates = self.get_selected_templates()
        selected_template = self.get_selected_template()

        # If no templates are currently selected, preserve the last saved templates
        if not selected_templates:
            selected_templates = self.config.get("last_templates", [])
            if not selected_templates and self.config.get("last_template"):
                selected_templates = [self.config.get("last_template", "")]

        # For backward compatibility, also keep the first template as "last_template"
        if selected_templates:
            selected_template = selected_templates[0]
        elif not selected_template:
            selected_template = self.config.get("last_template", "")

        config = {
            "template_directory": self.template_dir_var.get(),
            "last_template": selected_template,
            "last_templates": selected_templates,
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
            # refresh_templates() will restore the last_templates from config
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
        """Get the first selected template name (for compatibility)"""
        selection = self.template_listbox.curselection()
        if selection:
            return self.template_listbox.get(selection[0])
        return ""

    def get_selected_templates(self) -> list:
        """Get all selected template names"""
        selection = self.template_listbox.curselection()
        if selection:
            return [self.template_listbox.get(i) for i in selection]
        return []
    
    def select_template_by_name(self, template_name: str):
        """Select a template in the listbox by name"""
        for i in range(self.template_listbox.size()):
            if self.template_listbox.get(i) == template_name:
                self.template_listbox.selection_clear(0, tk.END)
                self.template_listbox.selection_set(i)
                self.template_listbox.see(i)
                break

    def select_templates_by_names(self, template_names: list):
        """Select multiple templates in the listbox by names"""
        self.template_listbox.selection_clear(0, tk.END)
        first_index = None
        for template_name in template_names:
            for i in range(self.template_listbox.size()):
                if self.template_listbox.get(i) == template_name:
                    self.template_listbox.selection_set(i)
                    if first_index is None:
                        first_index = i
                    break
        if first_index is not None:
            self.template_listbox.see(first_index)

    def on_template_selected(self, event):
        """Handle template selection event"""
        # Only save during user interaction, not during initialization
        if self.initializing:
            return

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
            # Save template directory to config (template selection will be saved when user selects one)
            self.save_config()
    
    def refresh_templates(self):
        """Refresh the list of available templates"""
        # Remember current selections before clearing
        current_selections = self.get_selected_templates()

        self.template_listbox.delete(0, tk.END)
        template_dir = self.template_dir_var.get()

        if not template_dir or not os.path.isdir(template_dir):
            return

        # Find all .xcf files in the directory
        templates = sorted([f for f in os.listdir(template_dir) if f.endswith('.xcf')])

        for template in templates:
            self.template_listbox.insert(tk.END, template)

        # Try to restore the last selected templates if they still exist
        # Use the saved config value, which should be up-to-date
        last_templates = self.config.get("last_templates", [])

        # Fallback to single template for backward compatibility
        if not last_templates and self.config.get("last_template"):
            last_templates = [self.config.get("last_template", "")]

        # Restore all saved templates that still exist
        if last_templates:
            for template_name in last_templates:
                if template_name in templates:
                    self.select_templates_by_names([t for t in last_templates if t in templates])
                    break
        elif current_selections:
            # If current selections still exist, keep them
            valid_selections = [t for t in current_selections if t in templates]
            if valid_selections:
                self.select_templates_by_names(valid_selections)
                # Save these selections to config
                self.config["last_templates"] = valid_selections
                self.config["last_template"] = valid_selections[0]
                self.save_config()
    
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
            self.save_config()
    
    def guess_year(self, month: int, day: int) -> int:
        """
        Guess the year for a given month and day.
        If the date is today or in the future this year, use this year.
        If the date is in the past this year, use next year.
        """
        today = datetime.now()
        current_year = today.year

        # Create date objects for this year and next year
        try:
            date_this_year = datetime(current_year, month, day)
        except ValueError:
            # Invalid date, use current year
            return current_year

        # Compare only date parts, ignoring time
        today_date = datetime(current_year, today.month, today.day)

        # If the date is today or in the future, use this year
        if date_this_year >= today_date:
            return current_year
        else:
            # Date is in the past, use next year
            return current_year + 1

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

        # Pattern 3: Month name formats (with or without year)
        month_names = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'june': '06', 'july': '07', 'august': '08', 'september': '09',
            'october': '10', 'november': '11', 'december': '12'
        }

        for month_name, month_num in month_names.items():
            # Pattern: "Dec 31, 2025" or "December 31, 2025" (with year)
            pattern = rf'\b{month_name}\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(\d{{4}})\b'
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                day, year = match.groups()
                return f"{year}-{month_num}-{day.zfill(2)}"

            # Pattern: "31 Dec 2025" or "31 December 2025" (with year)
            pattern = rf'\b(\d{{1,2}})(?:st|nd|rd|th)?\s+{month_name}\.?\s+(\d{{4}})\b'
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                day, year = match.groups()
                return f"{year}-{month_num}-{day.zfill(2)}"

            # Pattern: "Dec 31" or "December 31" (without year - guess year)
            pattern = rf'\b{month_name}\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?\b'
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                day = match.group(1)
                month = int(month_num)
                year = self.guess_year(month, int(day))
                return f"{year}-{month_num}-{day.zfill(2)}"

            # Pattern: "31 Dec" or "31 December" (without year - guess year)
            pattern = rf'\b(\d{{1,2}})(?:st|nd|rd|th)?\s+{month_name}\.?\b'
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                day = match.group(1)
                month = int(month_num)
                year = self.guess_year(month, int(day))
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
        """Main function to generate the banner(s) for selected template(s)"""
        # Remember the time value for next use
        time_value = self.time_entry.get()
        if time_value:
            self.last_time = time_value

        # Validate required fields
        if not self.template_dir_var.get():
            self.display_message("⚠ Error: Please select a template directory")
            return

        selected_templates = self.get_selected_templates()
        if not selected_templates:
            self.display_message("⚠ Error: Please select at least one template")
            return

        if not self.output_dir_var.get():
            self.display_message("⚠ Error: Please select an output directory")
            return

        if not self.title1_entry.get():
            self.display_message("⚠ Error: Title 1 is required")
            return

        if not self.speaker_name_entry.get():
            self.display_message("⚠ Error: Speaker Name is required")
            return

        if not self.date_entry.get():
            self.display_message("⚠ Error: Date is required")
            return

        if not self.time_entry.get():
            self.display_message("⚠ Error: Time is required")
            return

        # Validate speaker photo if provided
        photo_path = self.photo_path_var.get()
        if photo_path and not os.path.exists(photo_path):
            self.display_message(f"⚠ Error: Speaker photo not found: {photo_path}")
            return

        # Validate all selected templates exist
        for template_name in selected_templates:
            template_path = os.path.join(self.template_dir_var.get(), template_name)
            if not os.path.exists(template_path):
                self.display_message(f"⚠ Error: Template file not found: {template_path}")
                return

        # Generate banners for all selected templates
        date_text = self.date_entry.get()
        parsed_date = self.parse_date_from_text(date_text)
        title_slug = self.slugify(self.title1_entry.get(), 10)

        generated_files = []

        try:
            for template_name in selected_templates:
                template_path = os.path.join(self.template_dir_var.get(), template_name)
                template_slug = self.slugify(os.path.splitext(template_name)[0], 10)

                if parsed_date:
                    base_filename = f"{parsed_date}-{title_slug}-{template_slug}"
                else:
                    base_filename = f"banner-{title_slug}-{template_slug}"

                output_xcf = os.path.join(self.output_dir_var.get(), f"{base_filename}.xcf")
                output_jpg = os.path.join(self.output_dir_var.get(), f"{base_filename}.jpg")

                self.display_message(f"Generating banner with template: {template_name}...")

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
                    output_jpg=output_jpg
                )

                generated_files.append((base_filename, output_xcf))
                self.display_message(f"✓ Generated: {base_filename}")

            # Save config with current settings
            self.save_config()

            # Display summary message
            summary = f"✓ Successfully generated {len(generated_files)} banner(s)!"
            self.display_message(summary)

            # Open all generated XCF files in GIMP
            for _, output_xcf in generated_files:
                subprocess.Popen(['gimp', output_xcf])

        except subprocess.CalledProcessError:
            # Error already shown in copyable popup by update_banner, no need to show another
            pass
        except Exception as e:
            # Show generic errors in copyable popup instead of messagebox
            error_msg = f"An error occurred: {e}\n\n{type(e).__name__}: {str(e)}"
            self.root.after(100, lambda logs=error_msg: self.show_logs_popup("Error", logs))
    
    def generate_banner_script(self, template_path: str, title1: str, title2: str,
                               speaker_name: str, speaker_title: str, date: str, time: str,
                               photo_path: str, output_xcf: str, output_jpg: str) -> str:
        """
        Generate GIMP script for updating banner template.
        Uses the shared generate_banner_script_gimp3() function to ensure both GUI and auto
        versions generate identical scripts.
        """
        # Use the shared script generation function (which validates GIMP version internally)
        return generate_banner_script_gimp3(
            template_path=template_path,
            title1=title1,
            title2=title2,
            speaker_name=speaker_name,
            speaker_title=speaker_title,
            date=date,
            time=time,
            photo_path=photo_path,
            output_xcf=output_xcf,
            output_jpg=output_jpg
        )
    
    def update_banner(self, template_path: str, title1: str, title2: str,
                     speaker_name: str, speaker_title: str, date: str, time: str,
                     photo_path: str, output_xcf: str, output_jpg: str):
        """
        Use headless GIMP to update the template with provided values.
        Saves both XCF (with layers) and JPG (flattened) versions.
        """
        # Generate the script
        script = self.generate_banner_script(
            template_path, title1, title2, speaker_name, speaker_title,
            date, time, photo_path, output_xcf, output_jpg
        )
        
        # Write script to a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            script_file = f.name
            f.write(script)
        
        try:
            # Run GIMP in batch mode (with headless support)
            gimp_cmd = build_gimp_command(script_file)
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
            self.display_message("✓ Logs copied to clipboard!")
        
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
    
    def display_message(self, message: str):
        """Display a message in the status text area"""
        self.message_text.config(state=tk.NORMAL)
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.message_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.message_text.see(tk.END)  # Auto-scroll to bottom
        self.message_text.config(state=tk.DISABLED)

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
                self.display_message("⚠ Error: Please enter a template name")
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
                    self.display_message(f"⚠ Error: Invalid custom dimensions: {e}")
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
                # Display success message in status area
                success_msg = f"✓ Template '{template_name}' created successfully!\nDimensions: {width}x{height}\nOpening in GIMP for customization..."
                self.display_message(success_msg)
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
            # Load template
            script = load_gimp_template("template_create.py.template")
            
            # Calculate all the position values
            width_center = width // 2
            height_center = height // 2
            height_quarter = height // 4
            height_quarter_plus = height // 4 + int(height * 0.08)
            height_half_plus = height // 2 + int(height * 0.15)
            height_half_plus2 = height // 2 + int(height * 0.22)
            width_right = width - int(width * 0.15)
            height_bottom1 = height - int(height * 0.12)
            height_bottom2 = height - int(height * 0.06)
            height_third = height // 3
            height_two_thirds = 2 * height // 3
            
            font_size_title1 = int(width * 0.04)
            font_size_title2 = int(width * 0.025)
            font_size_speaker = int(width * 0.035)
            font_size_speaker_title = int(width * 0.02)
            font_size_date = int(width * 0.025)
            font_size_time = int(width * 0.02)
            
            # Format template with all values
            script = script.format(
                width=width,
                height=height,
                width_center=width_center,
                height_center=height_center,
                height_quarter=height_quarter,
                height_quarter_plus=height_quarter_plus,
                height_half_plus=height_half_plus,
                height_half_plus2=height_half_plus2,
                width_right=width_right,
                height_bottom1=height_bottom1,
                height_bottom2=height_bottom2,
                height_third=height_third,
                height_two_thirds=height_two_thirds,
                font_size_title1=font_size_title1,
                font_size_title2=font_size_title2,
                font_size_speaker=font_size_speaker,
                font_size_speaker_title=font_size_speaker_title,
                font_size_date=font_size_date,
                font_size_time=font_size_time,
                output_path=escape(output_path)
            )
        else:
            raise NotImplementedError("GIMP 2.x is not supported for template generation")
        
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
            gimp_cmd = build_gimp_command(script_file)
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


