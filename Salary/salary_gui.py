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
PERSONAL_DEDUCTION = 11_000_000
DEPENDENT_DEDUCTION = 4_400_000
HOURS_PER_MONTH = 176
INSURANCE_RATE = 0.105


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

    # Total salary - Internal excludes transport, mobifone, laptop
    if employee_type == "Internal":
        total_salary = gross_salary + bonus_oncall
        transport = 0  # Set to 0 for display
    else:
        total_salary = gross_salary + transport + MOBIFONE + LAPTOP + bonus_oncall

    # Insurance deduction
    insurance = gross_salary * INSURANCE_RATE

    # Taxable income
    taxable_income = total_salary - PERSONAL_DEDUCTION - (num_dependents * DEPENDENT_DEDUCTION) - insurance
    if taxable_income < 0:
        taxable_income = 0

    # Tax amount
    tax = calculate_progressive_tax(taxable_income)

    # Net salary
    net_salary = total_salary - insurance - tax + ot_amount

    return {
        'transport': transport,
        'total_salary': total_salary,
        'ot_amount': ot_amount,
        'insurance': insurance,
        'taxable_income': taxable_income,
        'tax': tax,
        'net_salary': net_salary
    }


class SalaryCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gross to Net Salary Calculator")
        self.root.geometry("500x800")
        self.root.minsize(500, 800)
        self.root.resizable(True, True)

        # Configure style
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Result.TLabel', font=('Arial', 12, 'bold'), foreground='#006400')
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="GROSS TO NET SALARY CALCULATOR", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="INPUT", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 15))

        # Employee Type selection
        type_frame = ttk.Frame(input_frame)
        type_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(type_frame, text="Employee Type:", width=25, anchor='w').pack(side=tk.LEFT)

        self.employee_type = tk.StringVar(value="Outsource")

        type_buttons_frame = ttk.Frame(type_frame)
        type_buttons_frame.pack(side=tk.RIGHT)

        ttk.Radiobutton(type_buttons_frame, text="Outsource", variable=self.employee_type, value="Outsource").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_buttons_frame, text="Internal", variable=self.employee_type, value="Internal").pack(side=tk.LEFT, padx=5)

        ttk.Separator(input_frame, orient='horizontal').pack(fill=tk.X, pady=5)

        # Input fields
        fields = [
            ("Gross Salary (VND):", "gross_salary"),
            ("Number of Dependents:", "dependents"),
            ("Bonus + On Call (VND):", "bonus"),
            ("OT 1.5 (hours):", "ot15"),
            ("OT 2.0 (hours):", "ot2"),
            ("OT 3.0 (hours):", "ot3"),
            ("Working Days:", "working_days"),
        ]

        self.entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            frame = ttk.Frame(input_frame)
            frame.pack(fill=tk.X, pady=3)

            label = ttk.Label(frame, text=label_text, width=25, anchor='w')
            label.pack(side=tk.LEFT)

            entry = ttk.Entry(frame, width=20)
            entry.pack(side=tk.RIGHT)

            # Set default values
            if field_name == 'working_days':
                entry.insert(0, "22")
            else:
                entry.insert(0, "0")

            # Auto-format numbers with dots for money fields
            if field_name in ['gross_salary', 'bonus']:
                entry.bind('<FocusOut>', lambda e, ent=entry: self.format_entry(ent))
                entry.bind('<Return>', lambda e, ent=entry: self.format_entry(ent))

            self.entries[field_name] = entry

        # Calculate button
        calc_button = ttk.Button(main_frame, text="CALCULATE", command=self.calculate)
        calc_button.pack(pady=15)

        # Output frame
        output_frame = ttk.LabelFrame(main_frame, text="OUTPUT", padding="15")
        output_frame.pack(fill=tk.X)

        # Output fields
        output_fields = [
            ("Transport:", "transport"),
            ("Total Salary:", "total_salary"),
            ("OT Amount:", "ot_amount"),
            ("Taxable Income:", "taxable_income"),
            ("Tax Amount (from Taxable):", "tax"),
            ("Insurance (10.5%):", "insurance"),
        ]

        self.output_labels = {}
        for label_text, field_name in output_fields:
            frame = ttk.Frame(output_frame)
            frame.pack(fill=tk.X, pady=2)

            label = ttk.Label(frame, text=label_text, width=20, anchor='w')
            label.pack(side=tk.LEFT)

            value_label = ttk.Label(frame, text="0", width=20, anchor='e')
            value_label.pack(side=tk.RIGHT)
            self.output_labels[field_name] = value_label

        # Separator
        ttk.Separator(output_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Net Salary result
        result_frame = ttk.Frame(output_frame)
        result_frame.pack(fill=tk.X, pady=5)

        ttk.Label(result_frame, text="NET SALARY:", style='Header.TLabel', width=20, anchor='w').pack(side=tk.LEFT)
        self.net_salary_label = ttk.Label(result_frame, text="0 VND", style='Result.TLabel', width=20, anchor='e')
        self.net_salary_label.pack(side=tk.RIGHT)

        # Net Salary big display with background
        self.net_frame = tk.Frame(main_frame, bg='#90EE90', pady=15)
        self.net_frame.pack(fill=tk.X, pady=15)

        tk.Label(self.net_frame, text="NET SALARY", font=('Arial', 12, 'bold'), bg='#90EE90').pack()
        self.net_salary_big = tk.Label(self.net_frame, text="0 VND", font=('Arial', 24, 'bold'), fg='#006400', bg='#90EE90')
        self.net_salary_big.pack(pady=5)

        # Note for Internal employees (always visible, text changes)
        self.note_label = tk.Label(self.net_frame, text="", font=('Arial', 11, 'italic'), fg='#8B0000', bg='#90EE90')
        self.note_label.pack(pady=(5, 0))

        # Clear button
        clear_button = ttk.Button(main_frame, text="CLEAR", command=self.clear)
        clear_button.pack(pady=10)

    def parse_number(self, value: str) -> float:
        """Parse number that may contain dots as thousand separators"""
        # Remove dots (thousand separator) and replace comma with dot for decimal
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

    def calculate(self):
        try:
            gross_salary = self.parse_number(self.entries['gross_salary'].get())
            num_dependents = int(self.entries['dependents'].get().replace('.', ''))
            bonus_oncall = self.parse_number(self.entries['bonus'].get())
            ot15 = float(self.entries['ot15'].get().replace(',', '.'))
            ot2 = float(self.entries['ot2'].get().replace(',', '.'))
            ot3 = float(self.entries['ot3'].get().replace(',', '.'))
            working_days = int(self.entries['working_days'].get())
            employee_type = self.employee_type.get()

            result = calculate_net_salary(gross_salary, num_dependents, bonus_oncall, ot15, ot2, ot3, working_days, employee_type)

            # Update output labels with dot separator
            self.output_labels['transport'].config(text=format_number(result['transport']))
            self.output_labels['total_salary'].config(text=format_number(result['total_salary']))
            self.output_labels['ot_amount'].config(text=format_number(result['ot_amount']))
            self.output_labels['insurance'].config(text=format_number(result['insurance']))
            self.output_labels['taxable_income'].config(text=format_number(result['taxable_income']))
            self.output_labels['tax'].config(text=format_number(result['tax']))
            self.net_salary_label.config(text=f"{format_number(result['net_salary'])} VND")
            self.net_salary_big.config(text=f"{format_number(result['net_salary'])} VND")

            # Show/hide note for Internal employees
            if employee_type == "Internal":
                self.note_label.config(text="(Please add gasoline allowance)")
            else:
                self.note_label.config(text="")

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")

    def clear(self):
        # Reset employee type
        self.employee_type.set("Outsource")

        for field_name, entry in self.entries.items():
            entry.delete(0, tk.END)
            if field_name == 'working_days':
                entry.insert(0, "22")
            else:
                entry.insert(0, "0")

        for label in self.output_labels.values():
            label.config(text="0")

        self.net_salary_label.config(text="0 VND")
        self.net_salary_big.config(text="0 VND")
        self.note_label.config(text="")  # Clear note


def main():
    root = tk.Tk()
    app = SalaryCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
