============================================
  Process CDD ZTE Tool
  Version 1.0.0
============================================

DESCRIPTION
-----------
A tool for processing CDD input files with SPU templates
to generate network configuration output files for ZTE equipment.


REQUIREMENTS
------------
- Windows 10/11
- Python 3.10 or higher (https://www.python.org/downloads/)
  IMPORTANT: During Python installation, check "Add Python to PATH"


INSTALLATION
------------
1. Extract the zip file to a folder (e.g., C:\Tools\Process_CDD_ZTE)

2. Double-click "install.bat" to install dependencies
   - This will create a virtual environment
   - Install all required Python packages

3. Wait for installation to complete


RUNNING THE APPLICATION
-----------------------
Option 1: Streamlit Web Interface (Recommended)
   - Double-click "run.bat"
   - The application will open in your default browser
   - URL: http://localhost:8501

Option 2: Tkinter Desktop Interface (Legacy)
   - Double-click "run_tkinter.bat"
   - A desktop window will open


HOW TO USE
----------
1. Select Input File:
   - Choose a CDD input file from the Input folder
   - Or upload your own file

2. Select Template:
   - Choose an SPU template from the Template folder

3. Process:
   - Click "Process SPU Output"
   - Output files will be saved in the Output folder
   - Files will automatically open after processing


FOLDER STRUCTURE
----------------
Tool/
  ├── Input/          <- Place your CDD input files here
  ├── Template/       <- SPU template files
  ├── Output/         <- Generated output files
  ├── src/            <- Source code (do not modify)
  ├── config.json     <- Configuration file (MME, AMF mappings)
  ├── install.bat     <- Run once to install
  ├── run.bat         <- Run the Streamlit app
  ├── run_tkinter.bat <- Run the Tkinter app
  └── requirements.txt


TROUBLESHOOTING
---------------
1. "Python is not installed" error:
   - Download Python from https://www.python.org/downloads/
   - During installation, CHECK "Add Python to PATH"
   - Restart your computer after installation

2. "Virtual environment not found" error:
   - Run install.bat first before running the application

3. Browser doesn't open automatically:
   - Manually open http://localhost:8501 in your browser

4. Port already in use:
   - Close other Streamlit applications
   - Or wait a few seconds and try again


SUPPORT
-------
For issues and questions, contact the development team.


============================================
