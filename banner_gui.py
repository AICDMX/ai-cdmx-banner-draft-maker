#!/usr/bin/env python3
"""
GIMP Banner Generator - Main Entry Point

Orchestrates the GUI and automatic banner generation functionality.
"""

import tkinter as tk
import argparse
import sys

from banner_gui_tk import BannerGeneratorGUI
from banner_auto import BannerGeneratorAuto


def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description='GIMP Banner Generator')
    parser.add_argument('--auto', action='store_true',
                       help='Run automatically using saved configuration (no GUI)')

    args = parser.parse_args()

    if args.auto:
        auto_gen = BannerGeneratorAuto()
        sys.exit(auto_gen.run_auto())
    else:
        root = tk.Tk()
        app = BannerGeneratorGUI(root)
        root.mainloop()


if __name__ == "__main__":
    main()
