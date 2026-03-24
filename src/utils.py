import requests


def isbn10_to_13(isbn10: str) -> str:
    """Convert an ISBN-10 to ISBN-13 by prepending 978 and recalculating the check digit."""
    digits = "".join(c for c in isbn10 if c.isdigit())[:9]
    prefix = "978" + digits
    total = sum(int(d) * (1 if i % 2 else 3) for i, d in enumerate(prefix))
    check = (10 - (total % 10)) % 10
    return prefix + str(check)


def isbn13_to_isbn10(isbn13: str) -> str:
    """Convert an ISBN-13 to ISBN-10 if it starts with 978, by stripping the prefix and recalculating the check digit."""
    digits = isbn13.replace("-", "").replace(" ", "")

    if len(digits) != 13 or not digits.startswith("978"):
        raise ValueError("Must be a valid 978-prefix ISBN-13")

    nine = digits[3:12]
    total = sum((i + 1) * int(d) for i, d in enumerate(nine))
    check = total % 11
    check_char = "X" if check == 10 else str(check)

    return nine + check_char


def fetch_openrouter_models(api_key: str, base_url: str) -> list[str]:
    """Fetch available models from OpenRouter API."""
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(f"{base_url}/models", headers=headers)
    response.raise_for_status()
    data = response.json()
    return [model["id"] for model in data["data"]]
