# Indian Home Loan Tax Benefits (FY 2025-26)

This document covers all tax deductions available for home loan borrowers in India.

---

## Section 24(b): Interest on Home Loan

This section allows for the deduction of interest paid on a home loan from "Income from House Property."

### Self-Occupied Property
- **Maximum Deduction**: ₹2,00,000 per financial year
- The property must be used for your own residence

### Let-Out (Rented) Property
- **Deduction**: The entire interest paid is deductible
- **Restriction**: The "Loss from House Property" that can be set off against other income heads is capped at ₹2,00,000

### Conditions
1. Construction/acquisition must be completed within **5 years** from the end of the financial year in which the capital was borrowed
2. Loan must be taken for purchase, construction, repair, renewal, or reconstruction

### Reduced Limit
- If the property is **not completed within 5 years**, the deduction drops to only ₹30,000 per year

---

## Section 80C: Principal Repayment

Deduction for repayment of principal amount of home loan.

### Limit
- Up to **₹1,50,000** per financial year
- This limit is **shared** with other 80C investments (PF, LIC, ELSS, PPF, etc.)

### Eligibility
- Only for **residential house property**
- Property must be in India

### Lock-in Period (5-Year Rule)
- **Critical**: If the property is sold within **5 years of possession**, all 80C deductions claimed previously will be **added back to your income** and taxed in the year of sale
- This is known as "clawback" provision

### Stamp Duty and Registration
- Expenses for stamp duty and registration charges can also be claimed under this ₹1.5 Lakh limit
- Must be claimed in the **year they are paid**

---

## Section 80EE: First-Time Buyer Incentive

Additional deduction for first-time home buyers.

### Details
| Feature | Section 80EE |
|---------|--------------|
| **Additional Limit** | ₹50,000 per year |
| **Loan Sanction Window** | FY 2016-17 only |
| **Stamp Value Limit** | Property value < ₹50 Lakh |
| **Loan Amount** | < ₹35 Lakh |
| **Requirement** | Must be a First-Time Buyer |

### Important Notes
- This is an **additional** deduction over and above the ₹2 Lakh limit of Section 24(b)
- Can be claimed until the loan is fully repaid
- First-time buyer = should not own any other residential property on the loan sanction date

---

## Section 80EEA: Affordable Housing Incentive

Enhanced deduction for first-time buyers of affordable housing.

### Details
| Feature | Section 80EEA |
|---------|---------------|
| **Additional Limit** | ₹1,50,000 per year |
| **Loan Sanction Window** | April 1, 2019 – March 31, 2022 |
| **Stamp Value Limit** | Property value < ₹45 Lakh |
| **Loan Amount** | No specific loan cap |
| **Requirement** | Must be a First-Time Buyer |

### Important Notes
- **Additional** to Section 24(b) limit
- First-time buyer = should not own any other residential property on the loan sanction date
- Cannot claim both 80EE and 80EEA simultaneously

---

## HRA + Home Loan: Can You Claim Both?

**Yes**, but under specific conditions. This is a common query.

### Scenario A: Different Cities
- You work in **City A** (paying rent)
- You own a home in **City B** (paying EMI)
- **Result**: You can claim **both** HRA and home loan benefits

### Scenario B: Same City
- You own a home but live in a rented house in the **same city**
- Reasons: Distance from workplace, family size, etc.
- **Result**: Technically allowed but **often scrutinized** by IT department
- **Requirement**: Taxpayer must prove a valid reason for not living in their own home

### Restriction
- You **cannot claim HRA** if you live in the **same house** for which you are claiming home loan benefits
- This would be considered a violation

---

## Under-Construction Property (Pre-EMI Interest)

Special rules for interest paid during the construction phase.

### Treatment During Construction
- Interest paid during construction **cannot be claimed** in the year it is paid
- All pre-construction interest is **aggregated**

### Deduction Timeline
- Claimed in **5 equal installments**
- Starting from the financial year in which **construction is completed**

### Example
If you paid ₹5 Lakh interest during 3 years of construction:
- Year 1 after completion: ₹1 Lakh (1/5th of ₹5 Lakh)
- Year 2 after completion: ₹1 Lakh
- ...and so on for 5 years

### Cap
- The sum of **current year's interest + 1/5th of pre-construction interest** must still fit within the **₹2 Lakh cap** for self-occupied properties

---

## How Genesis Calculates Tax Benefits

The Genesis model uses the following simplified approach:

```
yearly_interest_deduction = min(yearly_interest, 200000)  # Section 24(b) cap
yearly_principal_deduction = min(yearly_principal, 150000)  # Section 80C cap
total_deduction = interest_deduction + principal_deduction
tax_savings = total_deduction × tax_slab (30%)
```

### What Genesis Includes
- ✅ Section 24(b) interest deduction (₹2L cap)
- ✅ Section 80C principal deduction (₹1.5L cap)
- ✅ 30% tax bracket calculation

### What Genesis Does NOT Include
- ❌ Section 80EE/80EEA first-time buyer benefits
- ❌ Pre-EMI interest calculations
- ❌ Let-out property full interest deduction
- ❌ Joint home loan benefits
- ❌ HRA + Home Loan combination scenarios

### Maximum Annual Tax Saving in Genesis
- Interest: ₹2,00,000 × 30% = ₹60,000
- Principal: ₹1,50,000 × 30% = ₹45,000
- **Total**: Up to ₹1,05,000 per year

