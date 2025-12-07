"""
GIMP 3.0 Script Generation Module

Generates Python scripts for GIMP 3.0 to handle banner image manipulation.
This module separates the complex script generation logic from the GUI and auto modules.
"""

import subprocess
import os
import shutil
import re
from pathlib import Path


def escape_string(s):
    """Escape a string for use in Python f-strings."""
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def load_gimp_template(template_name: str) -> str:
    """
    Load a GIMP script template from the gimp_scripts directory.
    
    Args:
        template_name: Name of the template file (e.g., 'banner_generate_complete.py.template')
    
    Returns:
        Template content as string
    """
    script_dir = Path(__file__).parent / "gimp_scripts"
    template_path = script_dir / template_name
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_gimp_version() -> tuple:
    """
    Detect GIMP version by running gimp --version.
    Returns (major, minor) version tuple.
    Raises NotImplementedError if GIMP 2.x is detected or version detection fails.
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
            version_output = result.stdout.strip()
            match = re.search(r'(\d+)\.(\d+)', version_output)
            if match:
                major = int(match.group(1))
                minor = int(match.group(2))
                if major < 3:
                    raise NotImplementedError("GIMP 2.x is not supported")
                return (major, minor)
    except NotImplementedError:
        raise
    except Exception:
        pass
    raise NotImplementedError("GIMP version detection failed. GIMP 3.0+ is required.")


def build_gimp_command(script_file: str) -> list:
    """Build GIMP command for headless batch execution."""
    gimp_binary = 'gimp-console' if shutil.which('gimp-console') else 'gimp'
    gimp_cmd = [gimp_binary, '-i', '--batch-interpreter', 'python-fu-eval', '-b', f'exec(open("{script_file}").read())', '--quit']

    if shutil.which('xvfb-run'):
        return ['xvfb-run', '-a'] + gimp_cmd
    else:
        if not os.environ.get('DISPLAY'):
            gimp_cmd.insert(1, '--no-interface')
        return gimp_cmd


def generate_banner_script_gimp3(template_path, title1, title2, speaker_name,
                                  speaker_title, date, time, photo_path,
                                  output_xcf, output_png):
    """
    Generate a GIMP 3.0 compatible Python script for banner generation.

    Args:
        template_path: Path to the GIMP XCF template file
        title1: First title text
        title2: Second title text
        speaker_name: Speaker name text
        speaker_title: Speaker title text
        date: Date text
        time: Time text
        photo_path: Path to speaker photo (optional)
        output_xcf: Output path for XCF file
        output_png: Output path for PNG file

    Returns:
        Python script string for GIMP 3.0
    """
    # Load the template
    script = load_gimp_template("banner_generate_complete.py.template")

    # Format the template with escaped values
    script = script.format(
        template_path=escape_string(template_path),
        title1=escape_string(title1),
        title2=escape_string(title2),
        speaker_name=escape_string(speaker_name),
        speaker_title=escape_string(speaker_title),
        date=escape_string(date),
        time=escape_string(time),
        photo_path=escape_string(photo_path) if photo_path else "",
        output_xcf=escape_string(output_xcf),
        output_png=escape_string(output_png)
    )

    return script
