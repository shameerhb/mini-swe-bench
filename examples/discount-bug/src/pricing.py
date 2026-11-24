def apply_discount(price: float, discount: float) -> float:
    if discount > 100:
        raise ValueError("Discount cannot exceed 100")

    return price - (price * discount / 100)
