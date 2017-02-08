from typing import List, Dict


def has_valid_format(data: List[Dict]) -> bool:
    """
    Check data format, usually, from plugin results and return True if data
    format is value. False otherwise.
    """
    format_keys = ("library", "version", "severity", "summary", "advisory")

    # Check data is list instance
    if not hasattr(data, "append"):
        return False

    for x in data:
        # Check x is a dictionary
        if not hasattr(x, "keys"):
            return False

        if not len(set(format_keys).intersection(x.keys())) == len(format_keys):
            return False

    return True


__all__ = ("has_valid_format",)