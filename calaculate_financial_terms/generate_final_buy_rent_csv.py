import pandas as pd
from pathlib import Path

from modules.loan import average_interest_rate, amortization_yearly
from modules.tax import tax_savings
from modules.buy import buying_wealth
from modules.rent import lumpsum_growth, sip_future_value
from modules.compare import compare

# ===================== CONSTANTS =====================
DOWN_PAYMENT_RATE = 0.25
LOAN_YEARS = 20
TAX_SLAB = 0.30
APPRECIATION = 0.06
INVEST_RETURN = 0.10

BASE_DIR = Path(__file__).resolve().parent

# ===================== LOAD DATA =====================
df = pd.read_csv(BASE_DIR / "merged_real_estate_data_FINAL_CLEAN.csv")

# normalize column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# detect likely column names (flexible for different CSVs)
price_col = next((c for c in df.columns if "price_inr" in c or ("price" in c and "inr" in c)), None)
if price_col is None:
    price_col = next((c for c in df.columns if "price" in c), None)

area_col = next((c for c in df.columns if "area" in c), None)

rent_col = next((c for c in df.columns if "rent" in c), None)

# canonical numeric columns
df["price_inr"] = pd.to_numeric(df[price_col], errors="coerce") if price_col else pd.NA
df["area_sqft"] = pd.to_numeric(df[area_col], errors="coerce") if area_col else pd.NA
df["estimated_monthly_rent"] = pd.to_numeric(df[rent_col], errors="coerce") if rent_col else pd.NA

avg_rate = average_interest_rate(BASE_DIR / "banks.csv")

results = []

# ===================== PROCESS =====================
for _, row in df.iterrows():

    price = row["price_inr"]
    area = row["area_sqft"]
    rent = row["estimated_monthly_rent"]

    out = {
        "title": row["title"],
        "city": row["city"],
        "location": row["location"],
        "bedrooms": row["bedrooms"],
        "price_inr": price,
        "area_sqft": area,
        "estimated_monthly_rent": rent
    }

    # ---------- PRICE METRICS ----------
    if price > 0 and area > 0:
        price_lakhs = price / 100000
        out["price_lakhs"] = round(price_lakhs, 2)
        out["price_lakhs_psf"] = round(price_lakhs / area, 4)
    else:
        out["price_lakhs"] = None
        out["price_lakhs_psf"] = None

    # ---------- BUY VS RENT ----------
    if price > 0 and rent > 0:

        down_payment = price * DOWN_PAYMENT_RATE
        loan_amount = price - down_payment

        schedule, EMI = amortization_yearly(loan_amount, avg_rate)

        total_tax_saved = sum(
            tax_savings(y["interest"], y["principal"], TAX_SLAB)
            for y in schedule
        )

        total_emi_paid = EMI * 12 * LOAN_YEARS
        effective_emi = (total_emi_paid - total_tax_saved) / (12 * LOAN_YEARS)

        final_property_value = buying_wealth(price, APPRECIATION)

        fd_value = lumpsum_growth(down_payment, INVEST_RETURN)
        monthly_saving = max(EMI - rent, 0)
        sip_value = sip_future_value(monthly_saving, INVEST_RETURN)

        final_renting_wealth = fd_value + sip_value

        decision, diff = compare(final_property_value, final_renting_wealth)

        out.update({
            "down_payment": round(down_payment),
            "loan_amount": round(loan_amount),
            "monthly_emi": round(EMI),
            "effective_emi": round(effective_emi),
            "total_tax_saved": round(total_tax_saved),
            "final_property_value": round(final_property_value),
            "final_renting_wealth": round(final_renting_wealth),
            "decision": decision,
            "wealth_difference": round(diff)
        })
    else:
        out.update({
            "down_payment": None,
            "loan_amount": None,
            "monthly_emi": None,
            "effective_emi": None,
            "total_tax_saved": None,
            "final_property_value": None,
            "final_renting_wealth": None,
            "decision": None,
            "wealth_difference": None
        })

    results.append(out)

# ===================== SAVE =====================
final_df = pd.DataFrame(results)

output_dir = BASE_DIR / "output"
output_dir.mkdir(exist_ok=True)

final_df.to_csv(output_dir / "buy_vs_rent_FINAL_ANALYSIS.csv", index=False)

print(f"✅ SUCCESS: input rows = {len(df)}, output rows = {len(final_df)}")
