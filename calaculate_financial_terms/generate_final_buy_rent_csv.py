import pandas as pd
from pathlib import Path

from modules.loan import average_interest_rate, amortization_yearly, calculate_emi
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


def calculate_flip_thresholds(price, rent, down_payment, loan_amount, avg_rate, current_decision):
    """
    Calculate sensitivity thresholds - what would flip the decision.
    Returns dict with flip thresholds for interest rate, rent, and holding period.
    """
    thresholds = {
        "interest_rate_flip": None,
        "rent_flip": None,
        "holding_period_flip": None,
        "current_interest_rate": round(avg_rate, 2)
    }
    
    # Test interest rates from 5% to 15% in 0.5% steps
    for test_rate in [r/10 for r in range(50, 151, 5)]:  # 5.0% to 15.0%
        try:
            schedule, test_emi = amortization_yearly(loan_amount, test_rate)
            test_tax_saved = sum(
                tax_savings(y["interest"], y["principal"], TAX_SLAB)
                for y in schedule
            )
            test_final_property = buying_wealth(price, APPRECIATION)
            test_fd = lumpsum_growth(down_payment, INVEST_RETURN)
            test_monthly_saving = max(test_emi - rent, 0)
            test_sip = sip_future_value(test_monthly_saving, INVEST_RETURN)
            test_rent_wealth = test_fd + test_sip
            
            test_decision, _ = compare(test_final_property, test_rent_wealth)
            
            # Check if decision flipped
            if "BUY" in current_decision and "RENT" in test_decision:
                thresholds["interest_rate_flip"] = test_rate
                break
            elif "RENT" in current_decision and "BUY" in test_decision:
                thresholds["interest_rate_flip"] = test_rate
                break
        except:
            continue
    
    # Test rent levels (50% to 200% of current rent)
    for rent_mult in [m/100 for m in range(50, 201, 10)]:
        test_rent = rent * rent_mult
        try:
            schedule, EMI = amortization_yearly(loan_amount, avg_rate)
            test_final_property = buying_wealth(price, APPRECIATION)
            test_fd = lumpsum_growth(down_payment, INVEST_RETURN)
            test_monthly_saving = max(EMI - test_rent, 0)
            test_sip = sip_future_value(test_monthly_saving, INVEST_RETURN)
            test_rent_wealth = test_fd + test_sip
            
            test_decision, _ = compare(test_final_property, test_rent_wealth)
            
            if "BUY" in current_decision and "RENT" in test_decision:
                thresholds["rent_flip"] = round(test_rent)
                break
            elif "RENT" in current_decision and "BUY" in test_decision:
                thresholds["rent_flip"] = round(test_rent)
                break
        except:
            continue
    
    # Test holding periods (5, 10, 15, 20, 25, 30 years)
    for test_years in [5, 7, 10, 12, 15, 18, 20, 25, 30]:
        try:
            test_final_property = buying_wealth(price, APPRECIATION, test_years)
            test_fd = lumpsum_growth(down_payment, INVEST_RETURN, test_years)
            
            # For shorter periods, adjust loan tenure
            loan_tenure = min(test_years, LOAN_YEARS)
            schedule, EMI = amortization_yearly(loan_amount, avg_rate, loan_tenure)
            
            test_monthly_saving = max(EMI - rent, 0)
            test_sip = sip_future_value(test_monthly_saving, INVEST_RETURN, test_years)
            test_rent_wealth = test_fd + test_sip
            
            test_decision, _ = compare(test_final_property, test_rent_wealth)
            
            if "BUY" in current_decision and "RENT" in test_decision:
                thresholds["holding_period_flip"] = test_years
                break
            elif "RENT" in current_decision and "BUY" in test_decision:
                thresholds["holding_period_flip"] = test_years
                break
        except:
            continue
    
    return thresholds


# ===================== LOAD DATA =====================
df = pd.read_csv(BASE_DIR / "merged_real_estate_data_RAG_final.csv")

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
        
        # Calculate flip thresholds (sensitivity analysis)
        flip_thresholds = calculate_flip_thresholds(
            price, rent, down_payment, loan_amount, avg_rate, decision
        )

        out.update({
            "down_payment": round(down_payment),
            "loan_amount": round(loan_amount),
            "monthly_emi": round(EMI),
            "effective_emi": round(effective_emi),
            "total_tax_saved": round(total_tax_saved),
            "final_property_value": round(final_property_value),
            "final_renting_wealth": round(final_renting_wealth),
            "decision": decision,
            "wealth_difference": round(diff),
            # Flip thresholds for sensitivity
            "current_interest_rate": flip_thresholds["current_interest_rate"],
            "interest_rate_flip": flip_thresholds["interest_rate_flip"],
            "rent_flip": flip_thresholds["rent_flip"],
            "holding_period_flip": flip_thresholds["holding_period_flip"]
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
            "wealth_difference": None,
            "current_interest_rate": None,
            "interest_rate_flip": None,
            "rent_flip": None,
            "holding_period_flip": None
        })

    results.append(out)

# ===================== SAVE =====================
final_df = pd.DataFrame(results)

output_dir = BASE_DIR / "output"
output_dir.mkdir(exist_ok=True)

# Try to save, use alternate name if file is locked
try:
    final_df.to_csv(output_dir / "buy_vs_rent_FINAL_ANALYSIS.csv", index=False)
    print(f"✅ SUCCESS: input rows = {len(df)}, output rows = {len(final_df)}")
except PermissionError:
    final_df.to_csv(output_dir / "buy_vs_rent_FINAL_ANALYSIS_v2.csv", index=False)
    print(f"✅ SUCCESS: Saved as v2 (original file locked). input rows = {len(df)}, output rows = {len(final_df)}")
