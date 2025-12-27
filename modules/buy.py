def buying_wealth(property_price, appreciation_rate, years=20):
    return property_price * ((1 + appreciation_rate) ** years)
