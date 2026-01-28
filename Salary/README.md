# Salary Calculator - Gross to Net (Vietnam)

A simple GUI tool to calculate Net Salary from Gross Salary based on Vietnamese tax laws.

## Features

- Support for **Outsource** and **Internal** employee types
- Automatic number formatting with dots (e.g., 20.000.000)
- Progressive tax calculation (5% - 35%)
- OT calculation (1.5x, 2x, 3x rates)
- Transport allowance based on working days

## Input Fields

| Field | Description |
|-------|-------------|
| Employee Type | Outsource or Internal |
| Gross Salary (VND) | Monthly gross salary |
| Number of Dependents | For tax deduction |
| Bonus + On Call (VND) | Additional allowances |
| OT 1.5 (hours) | Overtime at 1.5x rate |
| OT 2.0 (hours) | Overtime at 2x rate |
| OT 3.0 (hours) | Overtime at 3x rate |
| Working Days | Number of working days (default: 22) |

## Calculation Formula

### For Outsource:
- **Total Salary** = Gross + Transport + Mobifone (450k) + Laptop (450k) + Bonus
- **Transport** = 1,760,000 (if >= 22 days) or 80,000 x days

### For Internal:
- **Total Salary** = Gross + Bonus (excludes Transport, Mobifone, Laptop)
- Note: "Please add gasoline allowance" is displayed

### Common:
- **Insurance** = Gross x 10.5% (BHXH 8% + BHYT 1.5% + BHTN 1%)
- **Taxable Income** = Total Salary - 11,000,000 - (Dependents x 4,400,000) - Insurance
- **OT Amount** = OT1.5 x (Gross/176) x 1.5 + OT2 x (Gross/176) x 2 + OT3 x (Gross/176) x 3
- **Net Salary** = Total Salary - Insurance - Tax + OT

### Tax Brackets (Progressive):
| Taxable Income | Rate |
|----------------|------|
| 0 - 5,000,000 | 5% |
| 5,000,001 - 10,000,000 | 10% |
| 10,000,001 - 18,000,000 | 15% |
| 18,000,001 - 32,000,000 | 20% |
| 32,000,001 - 52,000,000 | 25% |
| 52,000,001 - 80,000,000 | 30% |
| > 80,000,000 | 35% |

## Installation

### Windows (EXE)
1. Download `SalaryCalculator.exe` from [Releases](../../releases)
2. Double-click to run

### Python
```bash
python salary_gui.py
```

## Build EXE Locally

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "SalaryCalculator" salary_gui.py
```

The EXE will be in the `dist/` folder.

## GitHub Actions

The project includes a GitHub Actions workflow that automatically builds the Windows EXE:
- On every push to `main` branch
- On pull requests to `main`
- When a version tag is created (e.g., `v1.0.0`)

To create a release:
```bash
git tag v1.0.0
git push origin v1.0.0
```
