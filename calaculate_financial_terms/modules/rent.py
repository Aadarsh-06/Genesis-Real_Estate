def total_rent_paid(start_rent, escalation_rate, years=20):
    total = 0
    rent = start_rent

    for _ in range(years):
        total += rent * 12
        rent *= (1 + escalation_rate)

    return total

def lumpsum_growth(amount, annual_return, years=20):
    return amount * ((1 + annual_return) ** years)

def sip_future_value(monthly_sip, annual_return, years=20):
    months = years * 12
    r = annual_return / 12
    if r == 0:
        return monthly_sip * months
    return monthly_sip * (((1 + r)**months - 1) / r)
