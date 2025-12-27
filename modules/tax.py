def tax_savings(yearly_interest, yearly_principal, tax_slab):
    interest_deduction = min(yearly_interest, 200000)
    principal_deduction = min(yearly_principal, 150000)

    total_deduction = interest_deduction + principal_deduction
    savings = total_deduction * tax_slab

    return savings
