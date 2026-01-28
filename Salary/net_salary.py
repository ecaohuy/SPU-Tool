#!/usr/bin/env python3
"""
Gross to Net Salary Calculator - Vietnam
Input: Gross salary, Dependents, Bonus, OT hours
Output: Net Salary
"""

# Constants
MOBIFONE = 450_000
LAPTOP = 450_000
TRANSPORT = 1_760_000  # Assuming >= 22 working days
PERSONAL_DEDUCTION = 11_000_000
DEPENDENT_DEDUCTION = 4_400_000
HOURS_PER_MONTH = 176

# Insurance rates (total 10.5%)
INSURANCE_RATE = 0.105  # 8% + 1.5% + 1%


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


def calculate_net_salary(
    gross_salary: float,
    num_dependents: int,
    bonus_oncall: float,
    ot15: float,
    ot2: float,
    ot3: float
) -> float:
    """
    Calculate Net Salary from Gross Salary

    Args:
        gross_salary: Monthly gross salary (VND)
        num_dependents: Number of dependents for tax deduction
        bonus_oncall: Bonus + On Call Allowance (VND)
        ot15: OT 1.5x hours
        ot2: OT 2.0x hours
        ot3: OT 3.0x hours

    Returns:
        Net salary (VND)
    """
    # Calculate OT amount
    hourly_rate = gross_salary / HOURS_PER_MONTH
    ot_amount = (ot15 * hourly_rate * 1.5) + (ot2 * hourly_rate * 2) + (ot3 * hourly_rate * 3)

    # Total salary (for tax calculation)
    total_salary = gross_salary + TRANSPORT + MOBIFONE + LAPTOP + bonus_oncall

    # Insurance deduction
    insurance = gross_salary * INSURANCE_RATE

    # Taxable income
    taxable_income = total_salary - PERSONAL_DEDUCTION - (num_dependents * DEPENDENT_DEDUCTION) - insurance
    if taxable_income < 0:
        taxable_income = 0

    # Tax amount
    tax = calculate_progressive_tax(taxable_income)

    # Net salary = Total - Insurance - Tax + OT
    net_salary = total_salary - insurance - tax + ot_amount

    return net_salary


def main():
    print("\n" + "=" * 45)
    print("   GROSS TO NET SALARY CALCULATOR - VIETNAM")
    print("=" * 45)

    # Get inputs
    print("\nEnter your information:")
    gross_salary = float(input("  Gross Salary (VND): "))
    num_dependents = int(input("  Number of Dependents: "))
    bonus_oncall = float(input("  Bonus + On Call Allowance (VND): "))
    ot15 = float(input("  OT 1.5 (hours): "))
    ot2 = float(input("  OT 2.0 (hours): "))
    ot3 = float(input("  OT 3.0 (hours): "))

    # Calculate
    net_salary = calculate_net_salary(gross_salary, num_dependents, bonus_oncall, ot15, ot2, ot3)

    # Output
    print("\n" + "=" * 45)
    print(f"  NET SALARY: {net_salary:,.0f} VND")
    print("=" * 45 + "\n")


if __name__ == "__main__":
    main()
