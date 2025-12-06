"""
GIMP 3.0 Script Generation Module

Generates Python scripts for GIMP 3.0 to handle banner image manipulation.
This module separates the complex script generation logic from the GUI.
"""

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
        output_xcf=escape_string(output_xcf),
        output_png=escape_string(output_png)
    )
    
    return script
