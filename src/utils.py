import json
from datetime import datetime
from pathlib import Path
from typing import Final, Iterable

from dateutil import parser
from pytz import timezone

TIMEZONE: Final = "US/Pacific"
TODAY: Final = datetime.now(timezone(TIMEZONE)).strftime("%Y-%m-%d")  # replit is in UTC
INPUTS_DIR: Final = "INPUTS/"
SHEET_FILE: Final = "src/sheet_name.json"


def load_constants() -> dict:
    with open(SHEET_FILE, "r") as f:
        return json.load(f)


def save_constants(constants: dict) -> None:
    with open(SHEET_FILE, "w") as f:
        json.dump(constants, f, indent=2)


def get_latest_csv() -> Path:
    csv_all = Path(INPUTS_DIR).glob("*.csv")
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
    file = Path(INPUTS_DIR + value)
    if not file.is_file():
        return False
    return True


def filter_list(_list: list, filter_list: Iterable) -> list:
    return [i for i in _list if i not in filter_list]


def update_csv_isoformat(csv: str) -> None:
    """Update name to YYYYMMDD.csv format."""
    Path(csv).rename(f"{INPUTS_DIR}{TODAY}.csv")


def create_markdown(new_vendors: list, date: str) -> str:
    x = "\n- " + "\n- ".join(new_vendors)
    output = f"""Completed upload for {date}
    
    New Vendors

    {x}
    """
    return output
