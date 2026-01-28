#!/usr/bin/env python3
"""
Gross to Net Salary Calculator - Vietnam
Tkinter GUI Application
"""

import tkinter as tk
from tkinter import ttk, messagebox

# Constants
MOBIFONE = 450_000
LAPTOP = 450_000
TRANSPORT_FULL = 1_760_000
TRANSPORT_PER_DAY = 80_000
MIN_WORKING_DAYS = 22
PERSONAL_DEDUCTION = 15_500_000  # Updated from 01-Jan-2026
DEPENDENT_DEDUCTION = 6_200_000   # Updated from 01-Jan-2026
HOURS_PER_MONTH = 176
INSURANCE_RATE = 0.105
TRADE_UNION = 120_000  # For Internal employees only


def format_number(value: float) -> str:
    """Format number with dot as thousand separator (Vietnamese format)"""
    # Convert to integer string first
    num_str = str(int(value))
    # Add dots every 3 digits from right
    result = ""
    for i, digit in enumerate(reversed(num_str)):
        if i > 0 and i % 3 == 0:
            result = "." + result
        result = digit + result
    return result


def calculate_progressive_tax(taxable_income: float) -> float:
    """Calculate progressive tax based on Vietnam tax brackets"""
    if taxable_income <= 0:
        return 0

    brackets = [
        (5_000_000, 0.05),
        (5_000_000, 0.10),
        (8_000_000, 0.15),
        (14_000_000, 0.20),
        (20_000_000, 0.25),
        (28_000_000, 0.30),
        (float('inf'), 0.35)
    ]

    tax = 0
    remaining = taxable_income

    for bracket_amount, rate in brackets:
        if remaining <= 0:
            break
        taxable_in_bracket = min(remaining, bracket_amount)
        tax += taxable_in_bracket * rate
        remaining -= taxable_in_bracket

    return tax


def calculate_gross_from_net(target_net, num_dependents, bonus_oncall, ot15, ot2, ot3, working_days=22, employee_type="Outsource"):
    """Calculate Gross Salary from Net Salary using binary search"""
    # Initial bounds for binary search
    low = 0
    high = target_net * 3  # Upper bound estimate
    tolerance = 100  # Accuracy within 100 VND
    max_iterations = 100

    for _ in range(max_iterations):
        mid = (low + high) / 2
        result = calculate_net_salary(mid, num_dependents, bonus_oncall, ot15, ot2, ot3, working_days, employee_type)
        calculated_net = result['net_salary']

        if abs(calculated_net - target_net) < tolerance:
            # Found the gross salary, return full result
            result['gross_salary'] = mid
            return result
        elif calculated_net < target_net:
            low = mid
        else:
            high = mid

    # Return best estimate
    result = calculate_net_salary(mid, num_dependents, bonus_oncall, ot15, ot2, ot3, working_days, employee_type)
    result['gross_salary'] = mid
    return result


def calculate_net_salary(gross_salary, num_dependents, bonus_oncall, ot15, ot2, ot3, working_days=22, employee_type="Outsource"):
    """Calculate Net Salary from Gross Salary"""
    # Calculate Transport based on working days
    if working_days >= MIN_WORKING_DAYS:
        transport = TRANSPORT_FULL
    else:
        transport = TRANSPORT_PER_DAY * working_days

    # Calculate OT amount
    hourly_rate = gross_salary / HOURS_PER_MONTH
    ot_amount = (ot15 * hourly_rate * 1.5) + (ot2 * hourly_rate * 2) + (ot3 * hourly_rate * 3)

    # Total salary - Internal excludes transport, mobifone, laptop but has trade union
    if employee_type == "Internal":
        total_salary = gross_salary + bonus_oncall
        transport = 0  # Set to 0 for display
        mobifone = 0
        laptop = 0
        trade_union = TRADE_UNION
    else:
        total_salary = gross_salary + transport + MOBIFONE + LAPTOP + bonus_oncall
        mobifone = MOBIFONE
        laptop = LAPTOP
        trade_union = 0

    # Insurance deduction
    insurance = gross_salary * INSURANCE_RATE

    # Taxable income
    taxable_income = total_salary - PERSONAL_DEDUCTION - (num_dependents * DEPENDENT_DEDUCTION) - insurance
    if taxable_income < 0:
        taxable_income = 0

    # Tax amount
    tax = calculate_progressive_tax(taxable_income)

    # Net salary
    net_salary = total_salary - insurance - tax - trade_union + ot_amount

    return {
        'transport': transport,
        'mobifone': mobifone,
        'laptop': laptop,
        'total_salary': total_salary,
        'ot_amount': ot_amount,
        'insurance': insurance,
        'trade_union': trade_union,
        'taxable_income': taxable_income,
        'tax': tax,
        'net_salary': net_salary
    }


class SalaryCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Salary Calculator")
        self.root.geometry("550x750")
        self.root.minsize(500, 650)
        self.root.resizable(True, True)

        # Remove the default Python icon
        try:
            empty_icon = tk.PhotoImage(width=1, height=1)
            self.root.iconphoto(True, empty_icon)
        except:
            pass

        # Configure style
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Result.TLabel', font=('Arial', 12, 'bold'), foreground='#006400')
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Big.TButton', font=('Arial', 11, 'bold'))

        self.create_widgets()
        self.center_window()

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.gross_to_net_tab = ttk.Frame(self.notebook)
        self.net_to_gross_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.gross_to_net_tab, text="Gross to Net")
        self.notebook.add(self.net_to_gross_tab, text="Net to Gross")

        # Create content for each tab
        self.create_gross_to_net_tab()
        self.create_net_to_gross_tab()

    def create_gross_to_net_tab(self):
        """Create Gross to Net calculator tab"""
        # Create canvas with scrollbar
        canvas = tk.Canvas(self.gross_to_net_tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.gross_to_net_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def configure_canvas(event):
            canvas.itemconfig(canvas.find_all()[0], width=event.width)
        canvas.bind('<Configure>', configure_canvas)

        # Main content frame
        main_frame = ttk.Frame(scrollable_frame, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="GROSS TO NET CALCULATOR", style='Title.TLabel').pack(pady=(0, 10))

        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="INPUT", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # Employee Type
        type_frame = ttk.Frame(input_frame)
        type_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(type_frame, text="Employee Type:", width=22, anchor='w').pack(side=tk.LEFT)
        self.g2n_employee_type = tk.StringVar(value="Outsource")
        type_buttons = ttk.Frame(type_frame)
        type_buttons.pack(side=tk.RIGHT)
        ttk.Radiobutton(type_buttons, text="Outsource", variable=self.g2n_employee_type, value="Outsource").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_buttons, text="Internal", variable=self.g2n_employee_type, value="Internal").pack(side=tk.LEFT, padx=5)

        ttk.Separator(input_frame, orient='horizontal').pack(fill=tk.X, pady=5)

        # Input fields
        fields = [
            ("Gross Salary (VND):", "gross_salary", "0"),
            ("Number of Dependents:", "dependents", "0"),
            ("Bonus + On Call (VND):", "bonus", "0"),
            ("OT 1.5 (hours):", "ot15", "0"),
            ("OT 2.0 (hours):", "ot2", "0"),
            ("OT 3.0 (hours):", "ot3", "0"),
            ("Working Days:", "working_days", "22"),
        ]

        self.g2n_entries = {}
        for label_text, field_name, default in fields:
            frame = ttk.Frame(input_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=label_text, width=22, anchor='w').pack(side=tk.LEFT)
            entry = ttk.Entry(frame, width=18)
            entry.pack(side=tk.RIGHT)
            entry.insert(0, default)
            if field_name in ['gross_salary', 'bonus']:
                entry.bind('<FocusOut>', lambda e, ent=entry: self.format_entry(ent))
            self.g2n_entries[field_name] = entry

        # Calculate button
        ttk.Button(main_frame, text="CALCULATE", command=self.calculate_gross_to_net, style='Big.TButton').pack(pady=10, ipadx=20, ipady=5)

        # Output frame
        output_frame = ttk.LabelFrame(main_frame, text="OUTPUT", padding="10")
        output_frame.pack(fill=tk.X)

        output_fields = [
            ("Transport:", "transport"),
            ("Mobifone:", "mobifone"),
            ("Laptop:", "laptop"),
            ("Total Salary:", "total_salary"),
            ("OT Amount:", "ot_amount"),
            ("Taxable Income:", "taxable_income"),
            ("Tax Amount:", "tax"),
            ("Insurance (10.5%):", "insurance"),
            ("Trade Union:", "trade_union"),
        ]

        self.g2n_output_labels = {}
        for label_text, field_name in output_fields:
            frame = ttk.Frame(output_frame)
            frame.pack(fill=tk.X, pady=1)
            ttk.Label(frame, text=label_text, width=18, anchor='w').pack(side=tk.LEFT)
            value_label = ttk.Label(frame, text="0", width=18, anchor='e')
            value_label.pack(side=tk.RIGHT)
            self.g2n_output_labels[field_name] = value_label

        # NET SALARY display
        net_frame = tk.Frame(main_frame, bg='#90EE90', padx=20, pady=15)
        net_frame.pack(fill=tk.X, pady=15)
        tk.Label(net_frame, text="NET SALARY", font=('Arial', 14, 'bold'), bg='#90EE90').pack()
        self.g2n_net_salary = tk.Label(net_frame, text="0 VND", font=('Arial', 28, 'bold'), fg='#006400', bg='#90EE90')
        self.g2n_net_salary.pack(pady=8)
        self.g2n_note_label = tk.Label(net_frame, text="", font=('Arial', 11, 'italic'), fg='#8B0000', bg='#90EE90')
        self.g2n_note_label.pack()

        # Clear button
        ttk.Button(main_frame, text="CLEAR", command=self.clear_gross_to_net).pack(pady=10)

    def create_net_to_gross_tab(self):
        """Create Net to Gross calculator tab"""
        # Create canvas with scrollbar
        canvas = tk.Canvas(self.net_to_gross_tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.net_to_gross_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def configure_canvas(event):
            canvas.itemconfig(canvas.find_all()[0], width=event.width)
        canvas.bind('<Configure>', configure_canvas)

        # Main content frame
        main_frame = ttk.Frame(scrollable_frame, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="NET TO GROSS CALCULATOR", style='Title.TLabel').pack(pady=(0, 10))

        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="INPUT", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # Employee Type
        type_frame = ttk.Frame(input_frame)
        type_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(type_frame, text="Employee Type:", width=22, anchor='w').pack(side=tk.LEFT)
        self.n2g_employee_type = tk.StringVar(value="Outsource")
        type_buttons = ttk.Frame(type_frame)
        type_buttons.pack(side=tk.RIGHT)
        ttk.Radiobutton(type_buttons, text="Outsource", variable=self.n2g_employee_type, value="Outsource").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_buttons, text="Internal", variable=self.n2g_employee_type, value="Internal").pack(side=tk.LEFT, padx=5)

        ttk.Separator(input_frame, orient='horizontal').pack(fill=tk.X, pady=5)

        # Input fields
        fields = [
            ("Net Salary (VND):", "net_salary", "0"),
            ("Number of Dependents:", "dependents", "0"),
            ("Bonus + On Call (VND):", "bonus", "0"),
            ("OT 1.5 (hours):", "ot15", "0"),
            ("OT 2.0 (hours):", "ot2", "0"),
            ("OT 3.0 (hours):", "ot3", "0"),
            ("Working Days:", "working_days", "22"),
        ]

        self.n2g_entries = {}
        for label_text, field_name, default in fields:
            frame = ttk.Frame(input_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=label_text, width=22, anchor='w').pack(side=tk.LEFT)
            entry = ttk.Entry(frame, width=18)
            entry.pack(side=tk.RIGHT)
            entry.insert(0, default)
            if field_name in ['net_salary', 'bonus']:
                entry.bind('<FocusOut>', lambda e, ent=entry: self.format_entry(ent))
            self.n2g_entries[field_name] = entry

        # Calculate button
        ttk.Button(main_frame, text="CALCULATE", command=self.calculate_net_to_gross, style='Big.TButton').pack(pady=10, ipadx=20, ipady=5)

        # Output frame
        output_frame = ttk.LabelFrame(main_frame, text="OUTPUT", padding="10")
        output_frame.pack(fill=tk.X)

        output_fields = [
            ("Transport:", "transport"),
            ("Mobifone:", "mobifone"),
            ("Laptop:", "laptop"),
            ("Total Salary:", "total_salary"),
            ("OT Amount:", "ot_amount"),
            ("Taxable Income:", "taxable_income"),
            ("Tax Amount:", "tax"),
            ("Insurance (10.5%):", "insurance"),
            ("Trade Union:", "trade_union"),
        ]

        self.n2g_output_labels = {}
        for label_text, field_name in output_fields:
            frame = ttk.Frame(output_frame)
            frame.pack(fill=tk.X, pady=1)
            ttk.Label(frame, text=label_text, width=18, anchor='w').pack(side=tk.LEFT)
            value_label = ttk.Label(frame, text="0", width=18, anchor='e')
            value_label.pack(side=tk.RIGHT)
            self.n2g_output_labels[field_name] = value_label

        # GROSS SALARY display
        gross_frame = tk.Frame(main_frame, bg='#87CEEB', padx=20, pady=15)
        gross_frame.pack(fill=tk.X, pady=15)
        tk.Label(gross_frame, text="GROSS SALARY", font=('Arial', 14, 'bold'), bg='#87CEEB').pack()
        self.n2g_gross_salary = tk.Label(gross_frame, text="0 VND", font=('Arial', 28, 'bold'), fg='#00008B', bg='#87CEEB')
        self.n2g_gross_salary.pack(pady=8)
        self.n2g_note_label = tk.Label(gross_frame, text="", font=('Arial', 11, 'italic'), fg='#8B0000', bg='#87CEEB')
        self.n2g_note_label.pack()

        # Clear button
        ttk.Button(main_frame, text="CLEAR", command=self.clear_net_to_gross).pack(pady=10)

    def parse_number(self, value: str) -> float:
        """Parse number that may contain dots as thousand separators"""
        cleaned = value.replace('.', '').replace(',', '.')
        return float(cleaned) if cleaned else 0

    def format_entry(self, entry):
        """Format entry field with dots as thousand separators"""
        try:
            value = self.parse_number(entry.get())
            if value > 0:
                formatted = format_number(value)
                entry.delete(0, tk.END)
                entry.insert(0, formatted)
        except ValueError:
            pass

    def calculate_gross_to_net(self):
        """Calculate Net from Gross"""
        try:
            gross_salary = self.parse_number(self.g2n_entries['gross_salary'].get())
            num_dependents = int(self.g2n_entries['dependents'].get().replace('.', ''))
            bonus_oncall = self.parse_number(self.g2n_entries['bonus'].get())
            ot15 = float(self.g2n_entries['ot15'].get().replace(',', '.'))
            ot2 = float(self.g2n_entries['ot2'].get().replace(',', '.'))
            ot3 = float(self.g2n_entries['ot3'].get().replace(',', '.'))
            working_days = int(self.g2n_entries['working_days'].get())
            employee_type = self.g2n_employee_type.get()

            result = calculate_net_salary(gross_salary, num_dependents, bonus_oncall, ot15, ot2, ot3, working_days, employee_type)

            self.g2n_output_labels['transport'].config(text=format_number(result['transport']))
            self.g2n_output_labels['mobifone'].config(text=format_number(result['mobifone']))
            self.g2n_output_labels['laptop'].config(text=format_number(result['laptop']))
            self.g2n_output_labels['total_salary'].config(text=format_number(result['total_salary']))
            self.g2n_output_labels['ot_amount'].config(text=format_number(result['ot_amount']))
            self.g2n_output_labels['insurance'].config(text=format_number(result['insurance']))
            self.g2n_output_labels['trade_union'].config(text=format_number(result['trade_union']))
            self.g2n_output_labels['taxable_income'].config(text=format_number(result['taxable_income']))
            self.g2n_output_labels['tax'].config(text=format_number(result['tax']))
            self.g2n_net_salary.config(text=f"{format_number(result['net_salary'])} VND")

            if employee_type == "Internal":
                self.g2n_note_label.config(text="(Please add gasoline allowance)")
            else:
                self.g2n_note_label.config(text="")

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")

    def calculate_net_to_gross(self):
        """Calculate Gross from Net"""
        try:
            target_net = self.parse_number(self.n2g_entries['net_salary'].get())
            num_dependents = int(self.n2g_entries['dependents'].get().replace('.', ''))
            bonus_oncall = self.parse_number(self.n2g_entries['bonus'].get())
            ot15 = float(self.n2g_entries['ot15'].get().replace(',', '.'))
            ot2 = float(self.n2g_entries['ot2'].get().replace(',', '.'))
            ot3 = float(self.n2g_entries['ot3'].get().replace(',', '.'))
            working_days = int(self.n2g_entries['working_days'].get())
            employee_type = self.n2g_employee_type.get()

            result = calculate_gross_from_net(target_net, num_dependents, bonus_oncall, ot15, ot2, ot3, working_days, employee_type)

            self.n2g_output_labels['transport'].config(text=format_number(result['transport']))
            self.n2g_output_labels['mobifone'].config(text=format_number(result['mobifone']))
            self.n2g_output_labels['laptop'].config(text=format_number(result['laptop']))
            self.n2g_output_labels['total_salary'].config(text=format_number(result['total_salary']))
            self.n2g_output_labels['ot_amount'].config(text=format_number(result['ot_amount']))
            self.n2g_output_labels['insurance'].config(text=format_number(result['insurance']))
            self.n2g_output_labels['trade_union'].config(text=format_number(result['trade_union']))
            self.n2g_output_labels['taxable_income'].config(text=format_number(result['taxable_income']))
            self.n2g_output_labels['tax'].config(text=format_number(result['tax']))
            self.n2g_gross_salary.config(text=f"{format_number(result['gross_salary'])} VND")

            if employee_type == "Internal":
                self.n2g_note_label.config(text="(Please add gasoline allowance)")
            else:
                self.n2g_note_label.config(text="")

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")

    def clear_gross_to_net(self):
        """Clear Gross to Net tab"""
        self.g2n_employee_type.set("Outsource")
        for field_name, entry in self.g2n_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, "22" if field_name == 'working_days' else "0")
        for label in self.g2n_output_labels.values():
            label.config(text="0")
        self.g2n_net_salary.config(text="0 VND")
        self.g2n_note_label.config(text="")

    def clear_net_to_gross(self):
        """Clear Net to Gross tab"""
        self.n2g_employee_type.set("Outsource")
        for field_name, entry in self.n2g_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, "22" if field_name == 'working_days' else "0")
        for label in self.n2g_output_labels.values():
            label.config(text="0")
        self.n2g_gross_salary.config(text="0 VND")
        self.n2g_note_label.config(text="")


def main():
    root = tk.Tk()
    app = SalaryCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
