import pytest

from pricing import apply_discount


@pytest.mark.parametrize(
    "price,discount",
    [
        (-10, 10),
        (100, -5),
        (-1, -1),
    ],
)
def test_invalid_inputs_are_rejected(price, discount):
    with pytest.raises(ValueError):
        apply_discount(price, discount)
