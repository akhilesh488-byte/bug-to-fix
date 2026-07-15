def calculate_discount(price, percent):
    # BUG: dividing by 10 instead of 100
    #change this back to 10, if you are testing
    discount = price * percent / 100 # Corrected division
    return price - discount


def apply_tax(price, tax_rate):
    return price * (1 + tax_rate)


print(calculate_discount(100, 10))