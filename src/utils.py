from pathlib import Path
from dateutil import parser
from typing import Iterable


def get_latest_csv() -> Path:
    csv_all = Path("INPUTS/").glob("*.csv")
    try:
        return max(csv_all, key=Path.stat).name
    except ValueError:  # no csv files found
        return ""


def is_valid_date(value: str) -> bool:
    try:
        parser.parse(value)
    except parser.ParserError:
        return False
    else:
        return True


def is_valid_file(value: str) -> bool:
    file = Path("INPUTS/" + value)
    if not file.is_file():
        return False
    return True


def filter_list(_list: list, filter_list: Iterable) -> list:
    return [i for i in _list if i not in filter_list]


def retrieve_token() -> str:
    """Retrieve smartsheet API token from replit."""

    return os.environ["SS_TOKEN"]
