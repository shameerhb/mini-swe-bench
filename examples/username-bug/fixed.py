def normalize_username(username: str) -> str:
    normalized = username.strip().lower()
    if not normalized:
        raise ValueError("Username cannot be empty")
    return normalized
