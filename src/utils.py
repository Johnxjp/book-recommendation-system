def isbn10_to_13(isbn10: str) -> str:
    """Convert an ISBN-10 to ISBN-13 by prepending 978 and recalculating the check digit."""
    digits = "".join(c for c in isbn10 if c.isdigit())[:9]
    prefix = "978" + digits
    total = sum(int(d) * (1 if i % 2 else 3) for i, d in enumerate(prefix))
    check = (10 - (total % 10)) % 10
    return prefix + str(check)
