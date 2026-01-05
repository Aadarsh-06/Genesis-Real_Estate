import pandas as pd
import math

def average_interest_rate(csv_path):
    df = pd.read_csv(csv_path)
    return df["rate"].mean()

def calculate_emi(principal, annual_rate, tenure_years=20):
    R = annual_rate / (12 * 100)
    N = tenure_years * 12
    emi = principal * (R * (1 + R)**N) / ((1 + R)**N - 1)
    return emi

def amortization_yearly(principal, annual_rate, tenure_years=20):
    R = annual_rate / (12 * 100)
    EMI = calculate_emi(principal, annual_rate, tenure_years)

    balance = principal
    yearly = []

    for year in range(1, tenure_years + 1):
        interest_year = 0
        principal_year = 0

        for _ in range(12):
            interest = balance * R
            principal_paid = EMI - interest
            balance -= principal_paid

            interest_year += interest
            principal_year += principal_paid

        yearly.append({
            "year": year,
            "interest": interest_year,
            "principal": principal_year,
            "balance": max(balance, 0)
        })

    return yearly, EMI
