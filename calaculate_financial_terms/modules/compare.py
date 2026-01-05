def compare(buy_wealth, rent_wealth):
    if buy_wealth > rent_wealth:
        return "BUYING is financially better", buy_wealth - rent_wealth
    else:
        return "RENTING is financially better", rent_wealth - buy_wealth
