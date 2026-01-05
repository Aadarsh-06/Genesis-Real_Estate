import matplotlib.pyplot as plt

def plot_wealth(buy_values, rent_values):
    years = list(range(1, len(buy_values) + 1))

    plt.figure()
    plt.plot(years, buy_values)
    plt.plot(years, rent_values)

    plt.xlabel("Year")
    plt.ylabel("Wealth (₹)")
    plt.title("Buy vs Rent Wealth Comparison (20 Years)")
    plt.legend(["Buying", "Renting"])
    plt.grid(True)

    plt.show()
