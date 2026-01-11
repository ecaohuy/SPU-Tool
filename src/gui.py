"""Tkinter GUI Application for SPU Processing Tool - Modern UI."""

import os
import sys
import subprocess
import platform
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

from .excel_handler import ExcelHandler
from .processor import SPUProcessor
from .utils import get_input_folder, get_template_folder, get_output_folder


class ToolTip:
    """Create tooltips for widgets."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tooltip,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
            padx=5,
            pady=3
        )
        label.pack()

    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class SPUToolGUI:
    """Main GUI Application class with modern UI."""

    VERSION = "1.0.0"

    # Color scheme
    COLORS = {
        'primary': '#2196F3',       # Blue
        'primary_dark': '#1976D2',  # Dark Blue
        'success': '#4CAF50',       # Green
        'warning': '#FF9800',       # Orange
        'error': '#F44336',         # Red
        'bg_light': '#F5F5F5',      # Light Gray
        'bg_white': '#FFFFFF',      # White
        'text_dark': '#212121',     # Dark Gray
        'text_light': '#757575',    # Light Gray
        'border': '#E0E0E0',        # Border Gray
    }

    def __init__(self, root):
        self.root = root
        self.root.title("SPU Tool V1.0")
        self.root.geometry("1400x850")
        self.root.minsize(1200, 700)

        # Set window icon (if available)
        try:
            if platform.system() == "Windows":
                self.root.iconbitmap(default='')
        except:
            pass

        # Configure root background
        self.root.configure(bg=self.COLORS['bg_light'])

        # Initialize handlers
        self.excel_handler = ExcelHandler()
        self.processor = SPUProcessor()

        # File paths
        self.input_file_path = None
        self.template_file_path = None

        # Configure styles
        self._configure_styles()

        # Build UI
        self._create_widgets()

        # Center window
        self._center_window()

    def _center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _configure_styles(self):
        """Configure ttk styles for modern look."""
        self.style = ttk.Style()

        # Try to use a modern theme
        available_themes = self.style.theme_names()
        if 'clam' in available_themes:
            self.style.theme_use('clam')
        elif 'vista' in available_themes:
            self.style.theme_use('vista')

        # Configure custom styles
        self.style.configure(
            'Header.TLabel',
            font=('Segoe UI', 24, 'bold'),
            foreground=self.COLORS['primary'],
            background=self.COLORS['bg_white']
        )

        self.style.configure(
            'SubHeader.TLabel',
            font=('Segoe UI', 11),
            foreground=self.COLORS['text_light'],
            background=self.COLORS['bg_white']
        )

        self.style.configure(
            'Section.TLabelframe',
            background=self.COLORS['bg_white'],
            relief='flat'
        )

        self.style.configure(
            'Section.TLabelframe.Label',
            font=('Segoe UI', 11, 'bold'),
            foreground=self.COLORS['text_dark'],
            background=self.COLORS['bg_white']
        )

        self.style.configure(
            'Primary.TButton',
            font=('Segoe UI', 10, 'bold'),
            padding=(20, 10)
        )

        self.style.configure(
            'Success.TButton',
            font=('Segoe UI', 10, 'bold'),
            padding=(20, 10)
        )

        self.style.configure(
            'Action.TButton',
            font=('Segoe UI', 9),
            padding=(10, 5)
        )

        self.style.configure(
            'Status.TLabel',
            font=('Segoe UI', 10),
            padding=(5, 5)
        )

        self.style.configure(
            'FileStatus.TLabel',
            font=('Segoe UI', 10),
            padding=(10, 5)
        )

        self.style.configure(
            'TNotebook',
            background=self.COLORS['bg_light']
        )

        self.style.configure(
            'TNotebook.Tab',
            font=('Segoe UI', 9),
            padding=(10, 5)
        )

    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header section
        self._create_header(main_frame)

        # Content area (two columns)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

        # Left column: Controls
        left_frame = ttk.Frame(content_frame, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_frame.pack_propagate(False)

        self._create_input_section(left_frame)
        self._create_template_section(left_frame)
        self._create_process_section(left_frame)
        self._create_quick_actions(left_frame)

        # Right column: Data display
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._create_data_display(right_frame)

        # Bottom: Status bar
        self._create_status_bar(main_frame)

    def _create_header(self, parent):
        """Create header with title and version."""
        header_frame = tk.Frame(parent, bg=self.COLORS['bg_white'], relief='flat', bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Inner padding
        inner_frame = tk.Frame(header_frame, bg=self.COLORS['bg_white'], padx=20, pady=15)
        inner_frame.pack(fill=tk.X)

        # Title
        title_label = tk.Label(
            inner_frame,
            text="📊 SPU Tool V1.0",
            font=('Segoe UI', 22, 'bold'),
            fg=self.COLORS['primary'],
            bg=self.COLORS['bg_white']
        )
        title_label.pack(side=tk.LEFT)

        # Subtitle
        subtitle_label = tk.Label(
            inner_frame,
            text="SPU Planning Template Generator",
            font=('Segoe UI', 11),
            fg=self.COLORS['text_light'],
            bg=self.COLORS['bg_white']
        )
        subtitle_label.pack(side=tk.LEFT, padx=(15, 0), pady=(8, 0))

        # Version badge
        version_frame = tk.Frame(inner_frame, bg=self.COLORS['primary'], padx=10, pady=3)
        version_frame.pack(side=tk.RIGHT)

        version_label = tk.Label(
            version_frame,
            text=f"v{self.VERSION}",
            font=('Segoe UI', 9, 'bold'),
            fg='white',
            bg=self.COLORS['primary']
        )
        version_label.pack()

    def _create_input_section(self, parent):
        """Create the Input File section."""
        # Section frame with white background
        section_frame = tk.Frame(parent, bg=self.COLORS['bg_white'], relief='flat', bd=0)
        section_frame.pack(fill=tk.X, pady=(0, 10))

        inner_frame = tk.Frame(section_frame, bg=self.COLORS['bg_white'], padx=15, pady=15)
        inner_frame.pack(fill=tk.X)

        # Section title
        title_frame = tk.Frame(inner_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            title_frame,
            text="📁 Step 1: Select Input File",
            font=('Segoe UI', 12, 'bold'),
            fg=self.COLORS['text_dark'],
            bg=self.COLORS['bg_white']
        ).pack(side=tk.LEFT)

        # Status indicator
        self.input_status_label = tk.Label(
            title_frame,
            text="⚪ Not selected",
            font=('Segoe UI', 9),
            fg=self.COLORS['text_light'],
            bg=self.COLORS['bg_white']
        )
        self.input_status_label.pack(side=tk.RIGHT)

        # Button
        self.btn_select_input = ttk.Button(
            inner_frame,
            text="📂  Browse CDD Input File...",
            command=self._select_input_file,
            style='Primary.TButton',
            width=35
        )
        self.btn_select_input.pack(fill=tk.X, pady=(5, 10))
        ToolTip(self.btn_select_input, "Click to select your CDD input Excel file")

        # File display
        self.input_file_frame = tk.Frame(inner_frame, bg=self.COLORS['bg_light'], padx=10, pady=8)
        self.input_file_frame.pack(fill=tk.X)

        self.lbl_input_file = tk.Label(
            self.input_file_frame,
            text="No file selected",
            font=('Segoe UI', 9),
            fg=self.COLORS['text_light'],
            bg=self.COLORS['bg_light'],
            anchor='w'
        )
        self.lbl_input_file.pack(fill=tk.X)

    def _create_template_section(self, parent):
        """Create the Template section."""
        section_frame = tk.Frame(parent, bg=self.COLORS['bg_white'], relief='flat', bd=0)
        section_frame.pack(fill=tk.X, pady=(0, 10))

        inner_frame = tk.Frame(section_frame, bg=self.COLORS['bg_white'], padx=15, pady=15)
        inner_frame.pack(fill=tk.X)

        # Section title
        title_frame = tk.Frame(inner_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            title_frame,
            text="📋 Step 2: Select Template",
            font=('Segoe UI', 12, 'bold'),
            fg=self.COLORS['text_dark'],
            bg=self.COLORS['bg_white']
        ).pack(side=tk.LEFT)

        # Status indicator
        self.template_status_label = tk.Label(
            title_frame,
            text="⚪ Not selected",
            font=('Segoe UI', 9),
            fg=self.COLORS['text_light'],
            bg=self.COLORS['bg_white']
        )
        self.template_status_label.pack(side=tk.RIGHT)

        # Button
        self.btn_select_template = ttk.Button(
            inner_frame,
            text="📂  Browse SPU Template...",
            command=self._select_template_file,
            style='Primary.TButton',
            width=35
        )
        self.btn_select_template.pack(fill=tk.X, pady=(5, 10))
        ToolTip(self.btn_select_template, "Click to select your SPU template Excel file")

        # File display
        self.template_file_frame = tk.Frame(inner_frame, bg=self.COLORS['bg_light'], padx=10, pady=8)
        self.template_file_frame.pack(fill=tk.X)

        self.lbl_template_file = tk.Label(
            self.template_file_frame,
            text="No template selected",
            font=('Segoe UI', 9),
            fg=self.COLORS['text_light'],
            bg=self.COLORS['bg_light'],
            anchor='w'
        )
        self.lbl_template_file.pack(fill=tk.X)

    def _create_process_section(self, parent):
        """Create the Process section."""
        section_frame = tk.Frame(parent, bg=self.COLORS['bg_white'], relief='flat', bd=0)
        section_frame.pack(fill=tk.X, pady=(0, 10))

        inner_frame = tk.Frame(section_frame, bg=self.COLORS['bg_white'], padx=15, pady=15)
        inner_frame.pack(fill=tk.X)

        # Section title
        tk.Label(
            inner_frame,
            text="⚡ Step 3: Process Output",
            font=('Segoe UI', 12, 'bold'),
            fg=self.COLORS['text_dark'],
            bg=self.COLORS['bg_white']
        ).pack(anchor='w', pady=(0, 10))

        # Process button (large and prominent)
        self.btn_process = tk.Button(
            inner_frame,
            text="▶  PROCESS SPU OUTPUT",
            command=self._process_spu_output,
            font=('Segoe UI', 12, 'bold'),
            fg='white',
            bg=self.COLORS['success'],
            activebackground=self.COLORS['primary_dark'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=12
        )
        self.btn_process.pack(fill=tk.X, pady=(5, 10))
        ToolTip(self.btn_process, "Click to process and generate SPU output file")

        # Progress bar
        self.progress = ttk.Progressbar(
            inner_frame,
            mode='determinate',
            length=300
        )
        self.progress.pack(fill=tk.X, pady=(5, 0))

    def _create_quick_actions(self, parent):
        """Create quick action buttons."""
        section_frame = tk.Frame(parent, bg=self.COLORS['bg_white'], relief='flat', bd=0)
        section_frame.pack(fill=tk.X, pady=(0, 10))

        inner_frame = tk.Frame(section_frame, bg=self.COLORS['bg_white'], padx=15, pady=15)
        inner_frame.pack(fill=tk.X)

        # Section title
        tk.Label(
            inner_frame,
            text="🔧 Quick Actions",
            font=('Segoe UI', 12, 'bold'),
            fg=self.COLORS['text_dark'],
            bg=self.COLORS['bg_white']
        ).pack(anchor='w', pady=(0, 10))

        # Button row
        btn_frame = tk.Frame(inner_frame, bg=self.COLORS['bg_white'])
        btn_frame.pack(fill=tk.X)

        # Open Input Folder button
        btn_input = ttk.Button(
            btn_frame,
            text="📁 Input",
            command=lambda: self._open_folder(get_input_folder()),
            style='Action.TButton',
            width=10
        )
        btn_input.pack(side=tk.LEFT, padx=(0, 5))
        ToolTip(btn_input, "Open Input folder")

        # Open Template Folder button
        btn_template = ttk.Button(
            btn_frame,
            text="📋 Template",
            command=lambda: self._open_folder(get_template_folder()),
            style='Action.TButton',
            width=10
        )
        btn_template.pack(side=tk.LEFT, padx=(0, 5))
        ToolTip(btn_template, "Open Template folder")

        # Open Output Folder button
        btn_output = ttk.Button(
            btn_frame,
            text="📤 Output",
            command=lambda: self._open_folder(get_output_folder()),
            style='Action.TButton',
            width=10
        )
        btn_output.pack(side=tk.LEFT)
        ToolTip(btn_output, "Open Output folder")

    def _create_status_bar(self, parent):
        """Create the status bar."""
        status_frame = tk.Frame(parent, bg=self.COLORS['bg_white'], relief='flat', bd=0)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        inner_frame = tk.Frame(status_frame, bg=self.COLORS['bg_white'], padx=15, pady=10)
        inner_frame.pack(fill=tk.X)

        # Status icon and text
        self.lbl_status = tk.Label(
            inner_frame,
            text="✅ Ready - Select an input file to begin",
            font=('Segoe UI', 10),
            fg=self.COLORS['text_dark'],
            bg=self.COLORS['bg_white'],
            anchor='w'
        )
        self.lbl_status.pack(side=tk.LEFT)

        # Copyright
        tk.Label(
            inner_frame,
            text="SPU Tool V1.0 | Built with Python",
            font=('Segoe UI', 9),
            fg=self.COLORS['text_light'],
            bg=self.COLORS['bg_white']
        ).pack(side=tk.RIGHT)

    def _create_data_display(self, parent):
        """Create the tabbed data display area."""
        # Section frame
        section_frame = tk.Frame(parent, bg=self.COLORS['bg_white'], relief='flat', bd=0)
        section_frame.pack(fill=tk.BOTH, expand=True)

        inner_frame = tk.Frame(section_frame, bg=self.COLORS['bg_white'], padx=15, pady=15)
        inner_frame.pack(fill=tk.BOTH, expand=True)

        # Section title
        tk.Label(
            inner_frame,
            text="📊 Data Preview",
            font=('Segoe UI', 12, 'bold'),
            fg=self.COLORS['text_dark'],
            bg=self.COLORS['bg_white']
        ).pack(anchor='w', pady=(0, 10))

        # Notebook (tabbed view)
        self.notebook = ttk.Notebook(inner_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs for each sheet
        self.tabs = {}
        self.treeviews = {}

        sheet_names = [
            "IP", "Radio 2G", "Radio 3G", "Radio 4G", "Radio 5G",
            "2G-2G", "2G-3G", "2G-4G", "3G-2G", "3G-3G", "3G-4G",
            "RET", "Mapping"
        ]

        for sheet_name in sheet_names:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=f"  {sheet_name}  ")
            self.tabs[sheet_name] = tab

            # Create Treeview with scrollbars
            tree_frame = ttk.Frame(tab)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Scrollbars
            vsb = ttk.Scrollbar(tree_frame, orient="vertical")
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

            # Treeview with alternating row colors
            tree = ttk.Treeview(
                tree_frame,
                yscrollcommand=vsb.set,
                xscrollcommand=hsb.set,
                show="headings"
            )

            # Configure tag for alternating rows
            tree.tag_configure('oddrow', background='#F8F9FA')
            tree.tag_configure('evenrow', background='#FFFFFF')

            vsb.config(command=tree.yview)
            hsb.config(command=tree.xview)

            # Grid layout for better scrollbar positioning
            tree.grid(row=0, column=0, sticky='nsew')
            vsb.grid(row=0, column=1, sticky='ns')
            hsb.grid(row=1, column=0, sticky='ew')

            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)

            self.treeviews[sheet_name] = tree

    def _select_input_file(self):
        """Handle input file selection."""
        initial_dir = get_input_folder()
        if not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser("~")

        file_path = filedialog.askopenfilename(
            title="Select CDD Input File",
            initialdir=initial_dir,
            filetypes=[("Excel files", "*.xlsx *.xls *.xlsm"), ("All files", "*.*")]
        )

        if file_path:
            self.input_file_path = file_path
            filename = os.path.basename(file_path)
            self.lbl_input_file.config(text=filename, fg=self.COLORS['text_dark'])
            self.input_file_frame.config(bg='#E3F2FD')
            self.lbl_input_file.config(bg='#E3F2FD')
            self.input_status_label.config(text="✅ Selected", fg=self.COLORS['success'])
            self._update_status(f"📂 Loading: {filename}...")

            # Load the file in a separate thread
            thread = threading.Thread(target=self._load_input_file)
            thread.daemon = True
            thread.start()

    def _load_input_file(self):
        """Load input file in background thread."""
        try:
            # Read input file
            data = self.excel_handler.read_input_file(self.input_file_path)

            # Update processor
            self.processor.set_input_data(data)

            # Update UI in main thread
            self.root.after(0, self._populate_data_display, data)
            self.root.after(0, self._update_status, "✅ File loaded successfully! Select a template to continue.")

        except Exception as e:
            self.root.after(0, self._show_error, f"Failed to load file: {e}")

    def _populate_data_display(self, data):
        """Populate the data display tabs with loaded data."""
        for sheet_name, df in data.items():
            if sheet_name in self.treeviews:
                tree = self.treeviews[sheet_name]

                # Clear existing data
                tree.delete(*tree.get_children())

                if not df.empty:
                    # Set columns
                    columns = list(df.columns)
                    tree["columns"] = columns

                    # Configure column headers
                    for col in columns:
                        tree.heading(col, text=col)
                        tree.column(col, width=100, minwidth=50)

                    # Add rows with alternating colors (limit to first 1000 for performance)
                    for idx, row in df.head(1000).iterrows():
                        values = [str(v) if v is not None else "" for v in row.tolist()]
                        tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                        tree.insert("", tk.END, values=values, tags=(tag,))

    def _select_template_file(self):
        """Handle template file selection."""
        initial_dir = get_template_folder()
        if not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser("~")

        file_path = filedialog.askopenfilename(
            title="Select SPU Template File",
            initialdir=initial_dir,
            filetypes=[("Excel files", "*.xlsx *.xls *.xlsm"), ("All files", "*.*")]
        )

        if file_path:
            self.template_file_path = file_path
            filename = os.path.basename(file_path)
            self.lbl_template_file.config(text=filename, fg=self.COLORS['text_dark'])
            self.template_file_frame.config(bg='#E8F5E9')
            self.lbl_template_file.config(bg='#E8F5E9')
            self.template_status_label.config(text="✅ Selected", fg=self.COLORS['success'])
            self._update_status(f"📋 Template selected: {filename}")

            try:
                self.processor.set_template(file_path)
                if self.input_file_path:
                    self._update_status("✅ Ready to process! Click 'PROCESS SPU OUTPUT' to begin.")
            except Exception as e:
                self._show_error(f"Failed to load template: {e}")

    def _process_spu_output(self):
        """Handle SPU output processing."""
        # Validate inputs
        if not self.input_file_path:
            self._show_error("⚠️ Please select a CDD input file first (Step 1)")
            return

        if not self.template_file_path:
            self._show_error("⚠️ Please select an SPU template file first (Step 2)")
            return

        # Disable button during processing
        self.btn_process.config(state=tk.DISABLED, bg=self.COLORS['text_light'])
        self._update_status("⏳ Processing... Please wait.")
        self.progress["value"] = 0

        # Process in background thread
        thread = threading.Thread(target=self._run_processing)
        thread.daemon = True
        thread.start()

    def _run_processing(self):
        """Run processing in background thread."""
        try:
            def progress_callback(message, percentage):
                self.root.after(0, self._update_progress, message, percentage)

            output_files = self.processor.process(progress_callback)

            # Show success message
            files_list = "\n".join([os.path.basename(f) for f in output_files])
            self.root.after(0, self._show_success, f"✅ Output files created:\n\n{files_list}")

            # Automatically open output files
            for output_file in output_files:
                self.root.after(0, self._open_file, output_file)

        except Exception as e:
            self.root.after(0, self._show_error, f"❌ Processing failed: {e}")

        finally:
            self.root.after(0, self._reset_processing_state)

    def _update_progress(self, message, percentage):
        """Update progress bar and status."""
        self.lbl_status.config(text=f"⏳ {message}")
        self.progress["value"] = percentage

    def _reset_processing_state(self):
        """Reset UI after processing."""
        self.btn_process.config(state=tk.NORMAL, bg=self.COLORS['success'])

    def _update_status(self, message):
        """Update status label."""
        self.lbl_status.config(text=message)

    def _show_error(self, message):
        """Show error message."""
        self._update_status(f"❌ Error occurred")
        messagebox.showerror("Error", message)

    def _show_success(self, message):
        """Show success message."""
        self._update_status("✅ Processing complete!")
        self.progress["value"] = 100
        messagebox.showinfo("Success", message)

    def _open_file(self, file_path):
        """Open file with default application based on OS."""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", file_path], check=True)
        except Exception as e:
            self._update_status(f"⚠️ Could not open file: {e}")

    def _open_folder(self, folder_path):
        """Open folder with default file manager based on OS."""
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", folder_path], check=True)
        except Exception as e:
            self._show_error(f"Could not open folder: {e}")


def run_app():
    """Run the GUI application."""
    root = tk.Tk()

    # Set DPI awareness for Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    app = SPUToolGUI(root)
    root.mainloop()
