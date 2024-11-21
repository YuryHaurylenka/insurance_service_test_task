from datetime import date, datetime
from enum import Enum


def convert_to_serializable(data: dict) -> dict:
    """
    Recursively convert non-serializable objects (dates, enums) in a dictionary to serializable formats.

    Args:
        data (dict): Dictionary containing data to be converted.

    Returns:
        dict: A dictionary where all dates are ISO strings and enums are string values.
    """
    for key, value in data.items():
        if isinstance(value, (datetime, date)):
            data[key] = value.isoformat()
        elif isinstance(value, Enum):
            data[key] = value.value
        elif isinstance(value, dict):
            data[key] = convert_to_serializable(value)
    return data
