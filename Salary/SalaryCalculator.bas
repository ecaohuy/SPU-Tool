Attribute VB_Name = "SalaryCalculator"
Option Explicit

'====================================================================
' GROSS TO NET SALARY CALCULATOR - VIETNAM
' Author: VBA Tool
' Description: Calculate net salary from gross salary with Vietnamese tax law
'====================================================================

' Constants
Const MOBIFONE As Double = 450000
Const LAPTOP As Double = 450000
Const TRANSPORT_FULL As Double = 1760000
Const TRANSPORT_PER_DAY As Double = 80000
Const MIN_WORKING_DAYS As Integer = 22
Const PERSONAL_DEDUCTION As Double = 11000000
Const DEPENDENT_DEDUCTION As Double = 4400000
Const WORKING_HOURS_PER_MONTH As Double = 176

' Insurance rates
Const SOCIAL_INSURANCE_RATE As Double = 0.08
Const HEALTH_INSURANCE_RATE As Double = 0.015
Const UNEMPLOYMENT_INSURANCE_RATE As Double = 0.01

'====================================================================
' Main Function: Calculate Net Salary
'====================================================================
Public Function CalculateNetSalary(GrossSalary As Double, _
                                   NumDependents As Integer, _
                                   BonusAndOnCall As Double, _
                                   OT15Hours As Double, _
                                   OT2Hours As Double, _
                                   OT3Hours As Double, _
                                   Optional WorkingDays As Integer = 22) As Double

    Dim Transport As Double
    Dim TotalSalary As Double
    Dim OTAmount As Double
    Dim InsuranceDeduction As Double
    Dim TaxableIncome As Double
    Dim TaxAmount As Double
    Dim NetSalary As Double

    ' 1. Calculate Transport Allowance
    If WorkingDays >= MIN_WORKING_DAYS Then
        Transport = TRANSPORT_FULL
    Else
        Transport = TRANSPORT_PER_DAY * WorkingDays
    End If

    ' 2. Calculate Total Salary (for tax calculation)
    TotalSalary = GrossSalary + Transport + MOBIFONE + LAPTOP + BonusAndOnCall

    ' 3. Calculate OT Amount (non-taxable)
    OTAmount = CalculateOT(GrossSalary, OT15Hours, OT2Hours, OT3Hours)

    ' 4. Calculate Insurance Deductions
    InsuranceDeduction = GrossSalary * (SOCIAL_INSURANCE_RATE + HEALTH_INSURANCE_RATE + UNEMPLOYMENT_INSURANCE_RATE)

    ' 5. Calculate Taxable Income
    TaxableIncome = TotalSalary - PERSONAL_DEDUCTION - (NumDependents * DEPENDENT_DEDUCTION) - InsuranceDeduction

    ' Taxable income cannot be negative
    If TaxableIncome < 0 Then TaxableIncome = 0

    ' 6. Calculate Tax Amount (Progressive Tax)
    TaxAmount = CalculateProgressiveTax(TaxableIncome)

    ' 7. Calculate Net Salary
    ' Net = Total Salary - Insurance Deduction - Tax + OT
    NetSalary = TotalSalary - InsuranceDeduction - TaxAmount + OTAmount

    CalculateNetSalary = NetSalary

End Function

'====================================================================
' Calculate OT Amount
'====================================================================
Public Function CalculateOT(GrossSalary As Double, _
                            OT15Hours As Double, _
                            OT2Hours As Double, _
                            OT3Hours As Double) As Double

    Dim HourlyRate As Double
    Dim OTAmount As Double

    HourlyRate = GrossSalary / WORKING_HOURS_PER_MONTH

    OTAmount = (OT15Hours * HourlyRate * 1.5) + _
               (OT2Hours * HourlyRate * 2) + _
               (OT3Hours * HourlyRate * 3)

    CalculateOT = OTAmount

End Function

'====================================================================
' Calculate Progressive Tax (Vietnam Tax Brackets)
'====================================================================
Public Function CalculateProgressiveTax(TaxableIncome As Double) As Double

    Dim TaxAmount As Double

    If TaxableIncome <= 0 Then
        TaxAmount = 0
    ElseIf TaxableIncome <= 5000000 Then
        ' Level 1: 5%
        TaxAmount = TaxableIncome * 0.05
    ElseIf TaxableIncome <= 10000000 Then
        ' Level 2: 10%
        TaxAmount = 5000000 * 0.05 + (TaxableIncome - 5000000) * 0.1
    ElseIf TaxableIncome <= 18000000 Then
        ' Level 3: 15%
        TaxAmount = 5000000 * 0.05 + 5000000 * 0.1 + (TaxableIncome - 10000000) * 0.15
    ElseIf TaxableIncome <= 32000000 Then
        ' Level 4: 20%
        TaxAmount = 5000000 * 0.05 + 5000000 * 0.1 + 8000000 * 0.15 + (TaxableIncome - 18000000) * 0.2
    ElseIf TaxableIncome <= 52000000 Then
        ' Level 5: 25%
        TaxAmount = 5000000 * 0.05 + 5000000 * 0.1 + 8000000 * 0.15 + 14000000 * 0.2 + (TaxableIncome - 32000000) * 0.25
    ElseIf TaxableIncome <= 80000000 Then
        ' Level 6: 30%
        TaxAmount = 5000000 * 0.05 + 5000000 * 0.1 + 8000000 * 0.15 + 14000000 * 0.2 + 20000000 * 0.25 + (TaxableIncome - 52000000) * 0.3
    Else
        ' Level 7: 35%
        TaxAmount = 5000000 * 0.05 + 5000000 * 0.1 + 8000000 * 0.15 + 14000000 * 0.2 + 20000000 * 0.25 + 28000000 * 0.3 + (TaxableIncome - 80000000) * 0.35
    End If

    CalculateProgressiveTax = TaxAmount

End Function

'====================================================================
' Get Detailed Salary Breakdown
'====================================================================
Public Sub GetSalaryBreakdown(GrossSalary As Double, _
                              NumDependents As Integer, _
                              BonusAndOnCall As Double, _
                              OT15Hours As Double, _
                              OT2Hours As Double, _
                              OT3Hours As Double, _
                              Optional WorkingDays As Integer = 22)

    Dim Transport As Double
    Dim TotalSalary As Double
    Dim OTAmount As Double
    Dim InsuranceDeduction As Double
    Dim TaxableIncome As Double
    Dim TaxAmount As Double
    Dim NetSalary As Double
    Dim msg As String

    ' Calculate Transport
    If WorkingDays >= MIN_WORKING_DAYS Then
        Transport = TRANSPORT_FULL
    Else
        Transport = TRANSPORT_PER_DAY * WorkingDays
    End If

    ' Calculate components
    TotalSalary = GrossSalary + Transport + MOBIFONE + LAPTOP + BonusAndOnCall
    OTAmount = CalculateOT(GrossSalary, OT15Hours, OT2Hours, OT3Hours)
    InsuranceDeduction = GrossSalary * (SOCIAL_INSURANCE_RATE + HEALTH_INSURANCE_RATE + UNEMPLOYMENT_INSURANCE_RATE)
    TaxableIncome = TotalSalary - PERSONAL_DEDUCTION - (NumDependents * DEPENDENT_DEDUCTION) - InsuranceDeduction
    If TaxableIncome < 0 Then TaxableIncome = 0
    TaxAmount = CalculateProgressiveTax(TaxableIncome)
    NetSalary = TotalSalary - InsuranceDeduction - TaxAmount + OTAmount

    ' Build message
    msg = "===== SALARY BREAKDOWN =====" & vbCrLf & vbCrLf
    msg = msg & "INCOME:" & vbCrLf
    msg = msg & "  Gross Salary: " & Format(GrossSalary, "#,##0") & vbCrLf
    msg = msg & "  Transport: " & Format(Transport, "#,##0") & vbCrLf
    msg = msg & "  Mobifone: " & Format(MOBIFONE, "#,##0") & vbCrLf
    msg = msg & "  Laptop: " & Format(LAPTOP, "#,##0") & vbCrLf
    msg = msg & "  Bonus + On Call: " & Format(BonusAndOnCall, "#,##0") & vbCrLf
    msg = msg & "  OT Amount: " & Format(OTAmount, "#,##0") & vbCrLf
    msg = msg & "  --------------------------" & vbCrLf
    msg = msg & "  TOTAL INCOME: " & Format(TotalSalary + OTAmount, "#,##0") & vbCrLf & vbCrLf

    msg = msg & "DEDUCTIONS:" & vbCrLf
    msg = msg & "  Social Insurance (8%): " & Format(GrossSalary * SOCIAL_INSURANCE_RATE, "#,##0") & vbCrLf
    msg = msg & "  Health Insurance (1.5%): " & Format(GrossSalary * HEALTH_INSURANCE_RATE, "#,##0") & vbCrLf
    msg = msg & "  Unemployment (1%): " & Format(GrossSalary * UNEMPLOYMENT_INSURANCE_RATE, "#,##0") & vbCrLf
    msg = msg & "  Personal Tax Deduction: " & Format(PERSONAL_DEDUCTION, "#,##0") & vbCrLf
    msg = msg & "  Dependent Deduction (" & NumDependents & "): " & Format(NumDependents * DEPENDENT_DEDUCTION, "#,##0") & vbCrLf
    msg = msg & "  --------------------------" & vbCrLf
    msg = msg & "  Taxable Income: " & Format(TaxableIncome, "#,##0") & vbCrLf
    msg = msg & "  TAX AMOUNT: " & Format(TaxAmount, "#,##0") & vbCrLf & vbCrLf

    msg = msg & "============================" & vbCrLf
    msg = msg & "NET SALARY: " & Format(NetSalary, "#,##0") & vbCrLf
    msg = msg & "============================"

    MsgBox msg, vbInformation, "Salary Calculator"

End Sub

'====================================================================
' Setup Worksheet with Input Form
'====================================================================
Public Sub SetupSalarySheet()

    Dim ws As Worksheet

    ' Create or get the Salary Calculator sheet
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets("SalaryCalculator")
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Worksheets.Add
        ws.Name = "SalaryCalculator"
    End If
    On Error GoTo 0

    ' Clear existing content
    ws.Cells.Clear

    ' Set up headers and labels
    With ws
        ' Title
        .Range("B2").Value = "GROSS TO NET SALARY CALCULATOR"
        .Range("B2").Font.Bold = True
        .Range("B2").Font.Size = 16

        ' Input Section
        .Range("B4").Value = "INPUT"
        .Range("B4").Font.Bold = True
        .Range("B4").Interior.Color = RGB(200, 200, 255)

        .Range("B5").Value = "Gross Salary:"
        .Range("C5").Value = 0
        .Range("C5").NumberFormat = "#,##0"

        .Range("B6").Value = "Number of Dependents:"
        .Range("C6").Value = 0

        .Range("B7").Value = "Bonus + On Call Allowance:"
        .Range("C7").Value = 0
        .Range("C7").NumberFormat = "#,##0"

        .Range("B8").Value = "OT 1.5 (hours):"
        .Range("C8").Value = 0

        .Range("B9").Value = "OT 2.0 (hours):"
        .Range("C9").Value = 0

        .Range("B10").Value = "OT 3.0 (hours):"
        .Range("C10").Value = 0

        .Range("B11").Value = "Working Days:"
        .Range("C11").Value = 22

        ' Output Section
        .Range("B13").Value = "OUTPUT"
        .Range("B13").Font.Bold = True
        .Range("B13").Interior.Color = RGB(200, 255, 200)

        .Range("B14").Value = "Transport Allowance:"
        .Range("C14").Formula = "=IF(C11>=22,1760000,80000*C11)"
        .Range("C14").NumberFormat = "#,##0"

        .Range("B15").Value = "Total Salary:"
        .Range("C15").Formula = "=C5+C14+450000+450000+C7"
        .Range("C15").NumberFormat = "#,##0"

        .Range("B16").Value = "OT Amount:"
        .Range("C16").Formula = "=C8*(C5/176)*1.5+C9*(C5/176)*2+C10*(C5/176)*3"
        .Range("C16").NumberFormat = "#,##0"

        .Range("B17").Value = "Insurance Deduction (10.5%):"
        .Range("C17").Formula = "=C5*0.105"
        .Range("C17").NumberFormat = "#,##0"

        .Range("B18").Value = "Taxable Income:"
        .Range("C18").Formula = "=MAX(0,C15-11000000-C6*4400000-C17)"
        .Range("C18").NumberFormat = "#,##0"

        .Range("B19").Value = "Tax Amount:"
        .Range("C19").Formula = "=IF(C18<=0,0,IF(C18<=5000000,C18*0.05,IF(C18<=10000000,5000000*0.05+(C18-5000000)*0.1,IF(C18<=18000000,5000000*0.05+5000000*0.1+(C18-10000000)*0.15,IF(C18<=32000000,5000000*0.05+5000000*0.1+8000000*0.15+(C18-18000000)*0.2,IF(C18<=52000000,5000000*0.05+5000000*0.1+8000000*0.15+14000000*0.2+(C18-32000000)*0.25,IF(C18<=80000000,5000000*0.05+5000000*0.1+8000000*0.15+14000000*0.2+20000000*0.25+(C18-52000000)*0.3,5000000*0.05+5000000*0.1+8000000*0.15+14000000*0.2+20000000*0.25+28000000*0.3+(C18-80000000)*0.35)))))))"
        .Range("C19").NumberFormat = "#,##0"

        .Range("B21").Value = "NET SALARY:"
        .Range("B21").Font.Bold = True
        .Range("B21").Font.Size = 14
        .Range("C21").Formula = "=C15-C17-C19+C16"
        .Range("C21").NumberFormat = "#,##0"
        .Range("C21").Font.Bold = True
        .Range("C21").Font.Size = 14
        .Range("C21").Interior.Color = RGB(255, 255, 0)

        ' Adjust column widths
        .Columns("B").ColumnWidth = 30
        .Columns("C").ColumnWidth = 20

        ' Add borders
        .Range("B5:C11").Borders.LineStyle = xlContinuous
        .Range("B14:C19").Borders.LineStyle = xlContinuous
        .Range("B21:C21").Borders.LineStyle = xlContinuous
        .Range("B21:C21").Borders.Weight = xlMedium

        ' Highlight input cells
        .Range("C5:C11").Interior.Color = RGB(255, 255, 200)

    End With

    MsgBox "Salary Calculator sheet has been created!" & vbCrLf & _
           "Enter your values in the yellow cells (C5:C11)." & vbCrLf & _
           "Net Salary will be calculated automatically.", vbInformation, "Setup Complete"

End Sub

'====================================================================
' Quick Calculate - Use values from sheet
'====================================================================
Public Sub QuickCalculate()

    Dim ws As Worksheet
    Dim GrossSalary As Double
    Dim NumDependents As Integer
    Dim BonusAndOnCall As Double
    Dim OT15Hours As Double
    Dim OT2Hours As Double
    Dim OT3Hours As Double
    Dim WorkingDays As Integer

    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets("SalaryCalculator")
    On Error GoTo 0

    If ws Is Nothing Then
        MsgBox "Please run SetupSalarySheet first!", vbExclamation
        Exit Sub
    End If

    ' Get values from sheet
    GrossSalary = ws.Range("C5").Value
    NumDependents = ws.Range("C6").Value
    BonusAndOnCall = ws.Range("C7").Value
    OT15Hours = ws.Range("C8").Value
    OT2Hours = ws.Range("C9").Value
    OT3Hours = ws.Range("C10").Value
    WorkingDays = ws.Range("C11").Value

    ' Show breakdown
    Call GetSalaryBreakdown(GrossSalary, NumDependents, BonusAndOnCall, OT15Hours, OT2Hours, OT3Hours, WorkingDays)

End Sub
