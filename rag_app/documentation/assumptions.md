# Simulation Assumptions

This document describes all assumptions used in the Genesis Real Estate Buy vs Rent analysis.

---

## Financial Parameters

### Down Payment
- **Rate**: 25% of property price
- **Rationale**: Standard home loan requirement in India. Banks typically finance 75-80% of property value.

### Loan Tenure
- **Duration**: 20 years (240 months)
- **Rationale**: Most common home loan tenure in India, balancing EMI affordability with total interest paid.

### Property Appreciation Rate
- **Rate**: 6% per annum (compound)
- **Rationale**: Conservative estimate based on historical Indian real estate appreciation (typically 5-8% in metro cities).

### Investment Return Rate
- **Rate**: 10% per annum
- **Rationale**: Expected return from equity mutual funds/SIP over a 20-year horizon. Used to calculate opportunity cost of buying vs renting and investing.

### Tax Slab
- **Rate**: 30%
- **Rationale**: Highest income tax slab in India. Used to calculate maximum tax savings from home loan deductions.

---

## EMI Calculation

### Formula
EMI = P × R × (1+R)^N / ((1+R)^N - 1)

Where:
- **P** = Principal loan amount
- **R** = Monthly interest rate (annual rate / 12 / 100)
- **N** = Number of monthly installments (tenure × 12)

### Interest Rate
- Source: Average of major bank home loan rates from banks.csv
- Calculated using simple average of rates offered by SBI, HDFC, ICICI, and other major lenders

---

## Wealth Comparison (20-Year Outlook)

### Buying Scenario
**Final Property Value** = Property Price × (1 + Appreciation Rate)^20

Example: ₹1 Crore property at 6% appreciation = ₹3.21 Crore after 20 years

### Renting Scenario
**Final Renting Wealth** = FD Value + SIP Value

Where:
- **FD Value** = Down Payment × (1 + Investment Return)^20 (lumpsum investment)
- **SIP Value** = Monthly Savings × (((1+r)^months - 1) / r) (SIP future value)
- **Monthly Savings** = max(EMI - Rent, 0)

---

## Decision Logic

### When is BUYING better?
When Final Property Value > Final Renting Wealth

This means owning the property builds more wealth than:
- Investing the down payment
- Investing the monthly savings (EMI - Rent) via SIP

### When is RENTING better?
When Final Renting Wealth > Final Property Value

This means staying as a renter and investing builds more wealth than owning.

### Wealth Difference
The absolute difference between the two scenarios, indicating how much more wealth one option generates.

---

## Sensitivity Analysis (Flip Thresholds)

The system calculates what would flip the BUY/RENT decision:

### Interest Rate Flip
- Tested range: 5% to 15% in 0.5% steps
- Shows at what interest rate the decision would reverse

### Rent Flip
- Tested range: 50% to 200% of current rent in 10% steps
- Shows at what rent level the decision would reverse

### Holding Period Flip
- Tested periods: 5, 7, 10, 12, 15, 18, 20, 25, 30 years
- Shows minimum holding period needed for the decision to hold

