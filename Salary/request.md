 Change the gross salary to net salary by excel:
 1. Total salary = gross salary + transport + mobifone + laptop + Bonus + On call allowance
     - mobifone : 450.000
	 - laptop: 450.000
	 - transport : 1.760.000 if number of working day >=22 else  transport = 80.000 * number of working day

 5. Number of Dependent 
 6.OT 1.5
 7.OT 2
 8.OT 3
 9. Bonus + On call allowance
 OT = OT 1.5 * (Gross Salary)/176 * 1.5 + OT 2 * (Gross Salary)/176 * 2 + OT 3 * (Gross Salary)/176 * 3

Tax= Total salary -  15.500.000 - Number of Dependent  * 6.200.000 -   gross salary *  0.08 - gross salary * 0.015 - gross salary * 0.01
if Tax > 80000000 : TaxA =  (Tax - 80000000)  0.35  + 28.000.000 *0.3 + 20.000.00  * 0.25 + 14.000.000 * 0.2 + 8.000.000 * 0.15  * 5.000.000 * 0.1 + 5.000.000 *0.05
if  80.000.000 >= Tax > 52.000.000 : TaxA =  (Tax - 28.000.000) *0.3 + 20.000.00 * 0.25 + 14.000.000 * 0.2 + 8.000.000 * 0.15  * 5.000.000 * 0.1 + 5.000.000 *0.05
if  52.000.000 >= Tax > 32.000.000 : TaxA =  (Tax - 20.000.00) * 0.25 + 14.000.000 * 0.2 + 8.000.000 * 0.15  * 5.000.000 * 0.1 + 5.000.000 *0.05
if  32.000.000 >= Tax > 18.000.000 : TaxA =  (Tax - 14.000.000) * 0.2 + 8.000.000 * 0.15  * 5.000.000 * 0.1 + 5.000.000 *0.05
if  18.000.000 >= Tax > 10.000.000 : TaxA =  (Tax - 18.000.000) * 0.15  * 5.000.000 * 0.1 + 5.000.000 *0.05
if  10.000.000 >= Tax > 5.000.000 : TaxA =  (Tax - 5.000.000) * 0.1 + 5.000.000 *0.05
if Tax <= 5.000.000: TaxA = Tax*0.05
Net Salary = Tax - TaxA + OT 

 
 
 Please  create a VBA tool as request above with some input as below:
  - Gross salary  
  - Number of dependents
  - Bonus + On Call Allowance
  - OT 1.5
  - OT 2
  - OT 3
  
Output will be Net Salary
