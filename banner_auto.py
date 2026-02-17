"""
GIMP Banner Generator - Automatic (Non-GUI) Generation Module

Handles automated banner generation using saved configuration.
"""

import subprocess
import os
import re
import json
import sys
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime

from gimp_scripts_gimp3 import (
    generate_banner_script_gimp3,
    get_gimp_version,
    build_gimp_command
)


class BannerGeneratorAuto:
    """Non-GUI version for automatic banner generation"""
    
    def __init__(self):
        # Config file path for persistent settings
        self.config_dir = Path.home() / ".config" / "gimp-banner-generator"
        self.config_file = self.config_dir / "config.json"
        self.config = self.load_config()
    
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
                return {**default_config, **config}
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config file: {e}", file=sys.stderr)
            return default_config
    
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
        """Try to extract a date from free-form text and return YYYY-MM-DD format."""
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
        text = text[:max_length]
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = text.strip('-')
        return text or 'banner'
    

    def update_banner(self, template_path: str, title1: str, title2: str,
                     speaker_name: str, speaker_title: str, date: str, time: str,
                     photo_path: str, output_xcf: str, output_jpg: str):
        """Use headless GIMP to update the template with provided values."""
        # Generate script using the shared function
        script = generate_banner_script_gimp3(
            template_path, title1, title2, speaker_name, speaker_title,
            date, time, photo_path, output_xcf, output_jpg
        )

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            script_file = f.name
            f.write(script)

        try:
            gimp_cmd = build_gimp_command(script_file)
            
            env = os.environ.copy()
            env.pop('VIRTUAL_ENV', None)
            env.pop('VIRTUAL_ENV_PROMPT', None)
            if 'PYTHONPATH' in env and '.venv' in env['PYTHONPATH']:
                env.pop('PYTHONPATH', None)
            
            result = subprocess.run(
                gimp_cmd,
                capture_output=True,
                text=True,
                timeout=60,
                env=env
            )

            # Check if GIMP reported an error in stderr (but don't fail if it just complained about no return values)
            if result.returncode != 0 and 'returned no return values' not in result.stderr:
                raise subprocess.CalledProcessError(result.returncode, gimp_cmd, result.stdout, result.stderr)
            
            logs = []
            if result.stdout:
                logs.append("=== STDOUT ===\n")
                logs.append(result.stdout)
            if result.stderr:
                logs.append("\n=== STDERR ===\n")
                logs.append(result.stderr)
            
            log_output = "".join(logs) if logs else "No output from GIMP"
            print("=== GIMP Banner Generation Logs ===")
            print(log_output)
            print("=" * 40)
            
        except subprocess.TimeoutExpired as e:
            error_msg = (
                f"GIMP operation timed out after 60 seconds.\n\n"
                f"This might indicate:\n"
                f"- GIMP is stuck processing a large image\n"
                f"- The template file is corrupted or very large\n"
                f"- System resources are constrained\n"
            )
            print("=== GIMP Banner Generation Timeout ===", file=sys.stderr)
            print(error_msg, file=sys.stderr)
            raise
        except subprocess.CalledProcessError as e:
            logs = []
            if e.stdout:
                logs.append("=== STDOUT ===\n")
                logs.append(e.stdout)
            if e.stderr:
                logs.append("\n=== STDERR ===\n")
                logs.append(e.stderr)
            
            log_output = "".join(logs) if logs else f"Error: {e}"
            
            error_text = log_output.lower()
            if 'display' in error_text or 'gdk_display' in error_text:
                help_msg = (
                    "\n\n=== DISPLAY ERROR DETECTED ===\n"
                    "GIMP needs a display server to run. If you're running headless:\n"
                    "1. Install xvfb: sudo pacman -S xorg-server-xvfb (Arch) or sudo apt install xvfb (Ubuntu)\n"
                    "2. Or set DISPLAY environment variable if using X11 forwarding\n"
                )
                log_output += help_msg
            
            print("=== GIMP Banner Generation Error ===", file=sys.stderr)
            print(log_output, file=sys.stderr)
            print("=" * 40, file=sys.stderr)
            raise
        finally:
            try:
                os.unlink(script_file)
            except:
                pass
    
    def run_auto(self):
        """Run banner generation automatically using saved config"""
        # Validate required fields
        if not self.config.get("template_directory"):
            print("Error: No template directory configured. Please run the GUI first.", file=sys.stderr)
            return 1

        # Get template list - prefer multiple templates, fallback to single
        template_names = self.config.get("last_templates", [])
        if not template_names and self.config.get("last_template"):
            template_names = [self.config.get("last_template", "")]

        if not template_names:
            print("Error: No templates selected. Please run the GUI first and select a template.", file=sys.stderr)
            return 1

        if not self.config.get("output_directory"):
            print("Error: No output directory configured. Please run the GUI first.", file=sys.stderr)
            return 1

        if not self.config.get("title1"):
            print("Error: Title 1 is required. Please run the GUI first and fill in the form.", file=sys.stderr)
            return 1

        if not self.config.get("speaker_name"):
            print("Error: Speaker Name is required. Please run the GUI first and fill in the form.", file=sys.stderr)
            return 1

        if not self.config.get("date"):
            print("Error: Date is required. Please run the GUI first and fill in the form.", file=sys.stderr)
            return 1

        if not self.config.get("time"):
            self.config["time"] = "6-8PM"

        photo_path = self.config.get("photo_path", "")
        if photo_path and not os.path.exists(photo_path):
            print(f"Error: Speaker photo not found: {photo_path}", file=sys.stderr)
            return 1

        # Validate all templates exist
        for template_name in template_names:
            template_path = os.path.join(self.config["template_directory"], template_name)
            if not os.path.exists(template_path):
                print(f"Error: Template file not found: {template_path}", file=sys.stderr)
                return 1

        # Build common values
        date_text = self.config["date"]
        parsed_date = self.parse_date_from_text(date_text)
        title_slug = self.slugify(self.config["title1"], 10)

        generated_count = 0
        failed_count = 0

        # Generate banners for all selected templates
        for template_name in template_names:
            template_path = os.path.join(self.config["template_directory"], template_name)
            template_slug = self.slugify(os.path.splitext(template_name)[0], 10)

            if parsed_date:
                base_filename = f"{parsed_date}-{title_slug}-{template_slug}"
            else:
                base_filename = f"banner-{title_slug}-{template_slug}"

            output_xcf = os.path.join(self.config["output_directory"], f"{base_filename}.xcf")
            output_jpg = os.path.join(self.config["output_directory"], f"{base_filename}.jpg")

            # Generate the banner
            try:
                print(f"Generating banner from template: {template_name}")
                print(f"Output files:")
                print(f"  XCF: {output_xcf}")
                print(f"  JPG: {output_jpg}")
                print()

                self.update_banner(
                    template_path=template_path,
                    title1=self.config["title1"],
                    title2=self.config.get("title2", ""),
                    speaker_name=self.config["speaker_name"],
                    speaker_title=self.config.get("speaker_title", ""),
                    date=date_text,
                    time=self.config["time"],
                    photo_path=photo_path,
                    output_xcf=output_xcf,
                    output_jpg=output_jpg
                )

                print()
                print("=" * 40)
                print(f"✓ Banner generated successfully!")
                print(f"  XCF: {base_filename}.xcf")
                print(f"  JPG: {base_filename}.jpg")
                print("=" * 40)
                print()

                generated_count += 1

            except subprocess.CalledProcessError:
                print(f"Error: Banner generation failed for {template_name}. See logs above.", file=sys.stderr)
                failed_count += 1
            except Exception as e:
                print(f"Error: An unexpected error occurred for {template_name}: {e}", file=sys.stderr)
                failed_count += 1

        # Summary
        print()
        print("=" * 40)
        print(f"Summary: Generated {generated_count}/{len(template_names)} banner(s)")
        if failed_count > 0:
            print(f"Failed: {failed_count} banner(s)")
            print("=" * 40)
            return 1
        else:
            print("=" * 40)
            return 0


