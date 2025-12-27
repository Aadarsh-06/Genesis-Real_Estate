import pandas as pd

from modules.loan import average_interest_rate, amortization_yearly
from modules.tax import tax_savings
from modules.buy import buying_wealth
from modules.rent import total_rent_paid, lumpsum_growth, sip_future_value
from modules.compare import compare

# ===================== INPUTS =====================
CITY = "Bangalore"
TAX_SLAB = 0.30              # 30%
APPRECIATION = 0.06          # 6%
RENT_ESCALATION = 0.05       # 5%
INVEST_RETURN = 0.10         # 10%
DOWN_PAYMENT_RATE = 0.20

# ===================== LOAD DATA =====================
city_df = pd.read_csv("data/blrsuratpune-MB-analysis.csv")
city_data = city_df[city_df["City"] == CITY]
property_price = city_data["Price_INR"].mean()
monthly_rent = city_data["Estimated_Monthly_Rent"].mean()

down_payment = property_price * DOWN_PAYMENT_RATE
loan_amount = property_price - down_payment

# ===================== LOAN =====================
avg_rate = average_interest_rate("data/banks.csv")
schedule, EMI = amortization_yearly(loan_amount, avg_rate)

# ===================== TAX BENEFITS =====================
total_tax_saved = 0
for year in schedule:
    total_tax_saved += tax_savings(
        year["interest"],
        year["principal"],
        TAX_SLAB
    )

net_emi_paid = (EMI * 240) - total_tax_saved

# ===================== BUY CASE =====================
buy_wealth = buying_wealth(property_price, APPRECIATION)

# ===================== RENT CASE =====================
rent_paid = total_rent_paid(monthly_rent, RENT_ESCALATION)
fd_value = lumpsum_growth(down_payment, INVEST_RETURN)

monthly_saving = EMI - monthly_rent
sip_value = sip_future_value(monthly_saving, INVEST_RETURN)

rent_wealth = fd_value + sip_value

from modules.plots import plot_wealth

# ===================== WEALTH OVER TIME =====================
buy_wealth_yearly = []
rent_wealth_yearly = []

rent = monthly_rent
sip_monthly = EMI - monthly_rent
sip_total = 0
investment = down_payment

for year in range(1, 21):
    # BUY: property appreciation
    buy_wealth_yearly.append(
        property_price * ((1 + APPRECIATION) ** year)
    )

    # RENT:
    # Down payment growth
    investment *= (1 + INVEST_RETURN)

    # SIP yearly contribution
    sip_total += sip_monthly * 12 * ((1 + INVEST_RETURN) ** (20 - year))

    rent_wealth_yearly.append(investment + sip_total)

# ===================== FINAL COMPARISON =====================
decision, diff = compare(buy_wealth, rent_wealth)

# ===================== OUTPUT =====================
print(f"\nCITY: {CITY}")
print(f"Average Loan Rate: {avg_rate:.2f}%")
print(f"Monthly EMI: {EMI:,.0f}")
print(f"Net EMI Paid (after tax): {net_emi_paid:,.0f}")

print(f"\nBUY CASE Final Wealth: {buy_wealth:,.0f}")
print(f"RENT CASE Final Wealth: {rent_wealth:,.0f}")

print(f"\nDECISION: {decision}")
print(f"Wealth Difference: {diff:,.0f}")
plot_wealth(buy_wealth_yearly, rent_wealth_yearly)
