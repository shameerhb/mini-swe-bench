from username import normalize_username


def test_username_is_lowercase():
    assert normalize_username("Shameer") == "shameer"


def test_username_trims_spaces():
    assert normalize_username("  shameer  ") == "shameer"
