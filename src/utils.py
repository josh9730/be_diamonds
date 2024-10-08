import hashlib
from datetime import datetime
from typing import Final, Iterable

import yaml
from pytz import timezone
from tabulate import tabulate

SHEET_NAME_FILE: Final[str] = "src/sheet_name.yaml"
TIMEZONE: Final[str] = "US/Pacific"
TODAY: Final[str] = datetime.now(timezone(TIMEZONE)).strftime("%Y-%m-%d")  # replit is in UTC


def save_sheet_name(sheet_name: str, _type: str) -> None:
    with open(SHEET_NAME_FILE, "r") as f:
        data = yaml.safe_load(f)

    with open(SHEET_NAME_FILE, "w") as f:
        data.update({_type: sheet_name})
        yaml.safe_dump(data, f)


def save_df_output(df: "pd.DataFrame") -> None:
    """Save DataFrame as an table for reference."""
    df_format = tabulate(df, headers="keys", tablefmt="psql")
    with open("logs/df_output.txt", "w") as f:
        f.write(f"DATE: {TODAY}\n\n{df_format}")


def filter_list(_list: list, filter_list: Iterable) -> list:
    return [i for i in _list if i not in filter_list]


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()
