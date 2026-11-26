import pytest
from username import normalize_username


@pytest.mark.parametrize("username", ["", "   ", "\t"])
def test_empty_username_is_rejected(username):
    with pytest.raises(ValueError):
        normalize_username(username)
