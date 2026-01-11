#!/usr/bin/env python3
"""SPU Processing Tool - Tkinter Entry Point for PyInstaller.

This is the entry point for building a standalone Windows executable.
"""

import sys
import os

# Handle PyInstaller paths
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = os.path.dirname(sys.executable)
    # Add the application path to sys.path
    sys.path.insert(0, application_path)
    # Change to application directory for relative paths
    os.chdir(application_path)
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, application_path)

from src.gui import run_app


def main():
    """Main entry point for the SPU Processing Tool."""
    print("Starting SPU Processing Tool...")
    run_app()


if __name__ == "__main__":
    main()
