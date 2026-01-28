#!/usr/bin/env python3
"""
Gross to Net Salary Calculator - Vietnam
"""

# Constants
MOBIFONE = 450_000
LAPTOP = 450_000
TRANSPORT_FULL = 1_760_000
TRANSPORT_PER_DAY = 80_000
MIN_WORKING_DAYS = 22
PERSONAL_DEDUCTION = 11_000_000
DEPENDENT_DEDUCTION = 4_400_000
WORKING_HOURS_PER_MONTH = 176

# Insurance rates
SOCIAL_INSURANCE_RATE = 0.08
HEALTH_INSURANCE_RATE = 0.015
UNEMPLOYMENT_INSURANCE_RATE = 0.01


def calculate_ot(gross_salary: float, ot15_hours: float, ot2_hours: float, ot3_hours: float) -> float:
    """Calculate OT amount"""
    hourly_rate = gross_salary / WORKING_HOURS_PER_MONTH
    return (ot15_hours * hourly_rate * 1.5) + (ot2_hours * hourly_rate * 2) + (ot3_hours * hourly_rate * 3)


def calculate_progressive_tax(taxable_income: float) -> float:
    """Calculate progressive tax based on Vietnam tax brackets"""
    if taxable_income <= 0:
        return 0
    elif taxable_income <= 5_000_000:
        return taxable_income * 0.05
    elif taxable_income <= 10_000_000:
        return 5_000_000 * 0.05 + (taxable_income - 5_000_000) * 0.1
    elif taxable_income <= 18_000_000:
        return 5_000_000 * 0.05 + 5_000_000 * 0.1 + (taxable_income - 10_000_000) * 0.15
    elif taxable_income <= 32_000_000:
        return 5_000_000 * 0.05 + 5_000_000 * 0.1 + 8_000_000 * 0.15 + (taxable_income - 18_000_000) * 0.2
    elif taxable_income <= 52_000_000:
        return 5_000_000 * 0.05 + 5_000_000 * 0.1 + 8_000_000 * 0.15 + 14_000_000 * 0.2 + (taxable_income - 32_000_000) * 0.25
    elif taxable_income <= 80_000_000:
        return 5_000_000 * 0.05 + 5_000_000 * 0.1 + 8_000_000 * 0.15 + 14_000_000 * 0.2 + 20_000_000 * 0.25 + (taxable_income - 52_000_000) * 0.3
    else:
        return 5_000_000 * 0.05 + 5_000_000 * 0.1 + 8_000_000 * 0.15 + 14_000_000 * 0.2 + 20_000_000 * 0.25 + 28_000_000 * 0.3 + (taxable_income - 80_000_000) * 0.35


def calculate_net_salary(
    gross_salary: float,
    num_dependents: int,
    bonus_and_oncall: float,
    ot15_hours: float,
    ot2_hours: float,
    ot3_hours: float,
    working_days: int = 22
) -> dict:
    """Calculate net salary with full breakdown"""

    # Transport allowance
    if working_days >= MIN_WORKING_DAYS:
        transport = TRANSPORT_FULL
    else:
        transport = TRANSPORT_PER_DAY * working_days

    # Total salary (for tax calculation)
    total_salary = gross_salary + transport + MOBIFONE + LAPTOP + bonus_and_oncall

    # OT amount
    ot_amount = calculate_ot(gross_salary, ot15_hours, ot2_hours, ot3_hours)

    # Insurance deductions
    social_insurance = gross_salary * SOCIAL_INSURANCE_RATE
    health_insurance = gross_salary * HEALTH_INSURANCE_RATE
    unemployment_insurance = gross_salary * UNEMPLOYMENT_INSURANCE_RATE
    total_insurance = social_insurance + health_insurance + unemployment_insurance

    # Taxable income
    taxable_income = total_salary - PERSONAL_DEDUCTION - (num_dependents * DEPENDENT_DEDUCTION) - total_insurance
    if taxable_income < 0:
        taxable_income = 0

    # Tax amount
    tax_amount = calculate_progressive_tax(taxable_income)

    # Net salary
    net_salary = total_salary - total_insurance - tax_amount + ot_amount

    return {
        "gross_salary": gross_salary,
        "transport": transport,
        "mobifone": MOBIFONE,
        "laptop": LAPTOP,
        "bonus_and_oncall": bonus_and_oncall,
        "total_salary": total_salary,
        "ot_amount": ot_amount,
        "social_insurance": social_insurance,
        "health_insurance": health_insurance,
        "unemployment_insurance": unemployment_insurance,
        "total_insurance": total_insurance,
        "personal_deduction": PERSONAL_DEDUCTION,
        "dependent_deduction": num_dependents * DEPENDENT_DEDUCTION,
        "taxable_income": taxable_income,
        "tax_amount": tax_amount,
        "net_salary": net_salary
    }


def format_currency(amount: float) -> str:
    """Format number as Vietnamese currency"""
    return f"{amount:,.0f}"


def print_breakdown(result: dict):
    """Print salary breakdown"""
    print("\n" + "=" * 50)
    print("        GROSS TO NET SALARY BREAKDOWN")
    print("=" * 50)

    print("\nINCOME:")
    print(f"  Gross Salary:          {format_currency(result['gross_salary']):>15}")
    print(f"  Transport:             {format_currency(result['transport']):>15}")
    print(f"  Mobifone:              {format_currency(result['mobifone']):>15}")
    print(f"  Laptop:                {format_currency(result['laptop']):>15}")
    print(f"  Bonus + On Call:       {format_currency(result['bonus_and_oncall']):>15}")
    print(f"  OT Amount:             {format_currency(result['ot_amount']):>15}")
    print("  " + "-" * 35)
    print(f"  TOTAL INCOME:          {format_currency(result['total_salary'] + result['ot_amount']):>15}")

    print("\nDEDUCTIONS:")
    print(f"  Social Insurance (8%): {format_currency(result['social_insurance']):>15}")
    print(f"  Health Insurance (1.5%): {format_currency(result['health_insurance']):>13}")
    print(f"  Unemployment (1%):     {format_currency(result['unemployment_insurance']):>15}")
    print(f"  Personal Deduction:    {format_currency(result['personal_deduction']):>15}")
    print(f"  Dependent Deduction:   {format_currency(result['dependent_deduction']):>15}")
    print("  " + "-" * 35)
    print(f"  Taxable Income:        {format_currency(result['taxable_income']):>15}")
    print(f"  TAX AMOUNT:            {format_currency(result['tax_amount']):>15}")

    print("\n" + "=" * 50)
    print(f"  NET SALARY:            {format_currency(result['net_salary']):>15} VND")
    print("=" * 50 + "\n")


def main():
    import sys

    print("\n" + "=" * 50)
    print("    GROSS TO NET SALARY CALCULATOR - VIETNAM")
    print("=" * 50)

    # Check for command line arguments
    if len(sys.argv) >= 7:
        gross_salary = float(sys.argv[1])
        num_dependents = int(sys.argv[2])
        bonus_and_oncall = float(sys.argv[3])
        ot15_hours = float(sys.argv[4])
        ot2_hours = float(sys.argv[5])
        ot3_hours = float(sys.argv[6])
        working_days = int(sys.argv[7]) if len(sys.argv) > 7 else 22
    else:
        # Default example values
        print("\nUsage: python salary_calculator.py <gross> <dependents> <bonus> <ot1.5> <ot2> <ot3> [working_days]")
        print("\nRunning with example values...")
        gross_salary = 20_000_000
        num_dependents = 1
        bonus_and_oncall = 500_000
        ot15_hours = 10
        ot2_hours = 5
        ot3_hours = 0
        working_days = 22

    print(f"\nInputs:")
    print(f"  Gross Salary: {format_currency(gross_salary)}")
    print(f"  Dependents: {num_dependents}")
    print(f"  Bonus + On Call: {format_currency(bonus_and_oncall)}")
    print(f"  OT 1.5 hours: {ot15_hours}")
    print(f"  OT 2.0 hours: {ot2_hours}")
    print(f"  OT 3.0 hours: {ot3_hours}")
    print(f"  Working Days: {working_days}")

    result = calculate_net_salary(
        gross_salary, num_dependents, bonus_and_oncall,
        ot15_hours, ot2_hours, ot3_hours, working_days
    )

    print_breakdown(result)


if __name__ == "__main__":
    main()
