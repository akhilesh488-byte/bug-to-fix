def calculate_discount(price, percent):
    # BUG: dividing by 10 instead of 100
    discount = price * percent / 10
    return price - discount


def apply_tax(price, tax_rate):
    return price * (1 + tax_rate)

print(calculate_discount(100, 10))