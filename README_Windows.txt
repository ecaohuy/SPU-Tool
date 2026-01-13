============================================
  SPU Tool V1.0 - Windows Guide
============================================

This tool has TWO versions:
1. Tkinter (Desktop App) - SPU_Tool_V1.0.exe
2. Streamlit (Web App) - run_streamlit_windows.bat


=== OPTION 1: Tkinter Desktop App ===

Simply double-click: SPU_Tool_V1.0.exe

No installation required!


=== OPTION 2: Streamlit Web App ===

Requirements:
- Python 3.10 or higher (https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

Steps:
1. Double-click: run_streamlit_windows.bat
2. Wait for dependencies to install (first time only)
3. Open browser: http://localhost:8501
4. Press Ctrl+C in the command window to stop


=== OPTION 3: Streamlit with Docker ===

Requirements:
- Docker Desktop (https://www.docker.com/products/docker-desktop/)

Steps:
1. Open Command Prompt in this folder
2. Run: docker-compose -f docker-compose.streamlit.yml up -d
3. Open browser: http://localhost:8501
4. To stop: docker-compose -f docker-compose.streamlit.yml down


=== FOLDER STRUCTURE ===

Input/      - Place your CDD input files here
Output/     - Processed output files will be saved here
Template/   - SPU template files


=== TROUBLESHOOTING ===

Q: Streamlit won't start?
A: Make sure Python is installed and added to PATH.
   Try running: python --version

Q: Port 8501 already in use?
A: Change the port in run_streamlit_windows.bat or
   docker-compose.streamlit.yml

Q: Missing dependencies?
A: Delete .venv folder and run the batch file again.


============================================
  SPU Tool V1.0 | Built with Python
============================================
