def is_number(s) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False
