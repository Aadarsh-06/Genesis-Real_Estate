# Decision Logic Documentation

This document explains how the Genesis system makes BUY vs RENT recommendations.

---

## Core Principle

The decision is based on **wealth maximization over a 20-year horizon**.

We compare two scenarios:
1. **Buy the property** - Build equity through ownership and appreciation
2. **Rent and invest** - Stay flexible, invest the saved capital in financial instruments

---

## Scenario 1: Buying

### Initial Investment
- **Down Payment**: 25% of property price (paid upfront)
- **Loan Amount**: 75% of property price (financed through home loan)

### Monthly Costs
- **EMI**: Fixed monthly payment covering principal + interest
- **Effective EMI**: EMI minus monthly tax benefit equivalent

### 20-Year Outcome
- **Final Property Value** = Current Price × (1.06)^20
- You own a fully paid-off asset worth approximately 3.2× the original price

### Benefits of Buying
- Asset ownership and security
- Tax deductions on interest (Section 24b) and principal (Section 80C)
- Protection against rent inflation
- Forced savings discipline

---

## Scenario 2: Renting

### Initial Investment
- **Down Payment Invested**: The 25% that would have been down payment goes into a lumpsum investment earning 10% annually

### Monthly Savings
- **Savings** = EMI - Rent (if EMI > Rent)
- These savings are invested via SIP at 10% annual return

### 20-Year Outcome
- **FD/Lumpsum Value** = Down Payment × (1.10)^20
- **SIP Value** = Monthly Savings invested for 20 years
- **Total Renting Wealth** = FD Value + SIP Value

### Benefits of Renting
- Flexibility to relocate
- No maintenance/repair costs
- Capital available for other investments
- No property-related risks

---

## The Decision

### BUY is recommended when:
Final Property Value > Final Renting Wealth

**Translation**: The property appreciation plus tax benefits outweigh what you could earn by investing.

### RENT is recommended when:
Final Renting Wealth > Final Property Value

**Translation**: Investing your capital generates more wealth than property ownership.

---

## Wealth Difference

The **Wealth Difference** shown is the absolute value of:

|Final Property Value - Final Renting Wealth|

This represents how much more money you would have by choosing the recommended option.

---

## Key Factors Affecting the Decision

1. **Property Price to Rent Ratio**
   - High rent relative to EMI favors buying
   - Low rent relative to EMI favors renting

2. **Interest Rate**
   - Higher rates increase EMI, making renting more attractive
   - Lower rates reduce EMI, making buying more attractive

3. **Location Appreciation Potential**
   - High-growth areas favor buying
   - Stagnant markets favor renting

4. **Holding Period**
   - Longer holding periods favor buying (appreciation compounds)
   - Shorter periods favor renting (transaction costs matter)

---

## Important Notes

1. This analysis assumes you WILL invest the savings if you rent
2. Tax benefits assume 30% tax bracket
3. Actual appreciation may vary by location
4. This is a financial model, not considering lifestyle preferences

