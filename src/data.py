from pathlib import Path

import pandas as pd
import validators


def bool_fields_test(test_val: bool, reverse: bool):
    """Convert values to bool or pd.NA. Intent is to put valids in one Series and invalids in another,
    which will be used by pandas count() aggregator.

    test_val: essentially a bool based on a previous test
    reverse: Inverses the check. This allows for creating pd.Series with True values when the test is False.
             Example: If url is valid and not reverse -> one pd.Series as True while other values are pd.NA. If url is
             invalid and reverse -> the other pd.Series as True while valid links are pd.NA
    return: True or pd.NA
    """
    if (test_val and not reverse) or (not test_val and reverse):
        return True
    return pd.NA


def check_video_field(val: str, reverse: bool):
    test = val == "Y"
    return bool_fields_test(test, reverse)


def check_url_field(url: str, reverse: bool):
    """
    Invalid URL:
        - any of test_strings in URL
        - shorter than 6 characters
        - not a valid URL
    """
    if not validators.url(url):  # handle invalid types
        url = ""

    test_strings = ("diacam", "mp4", "gem360")
    test = not (any(i in url for i in test_strings) or len(url) < 6)
    return bool_fields_test(test, reverse)


def create_output_df(csv_path: Path) -> pd.DataFrame:
    """Load fields from CSV and group (sum) by Vendor.

    From CSV:
    - Video URL from Vendor: expected to be URLs or blank
    - Video Upload: expected to be Y or N

    Output DF:
    - Valid V360: count of valid URLs
    - Blank/Invalid: count of invalid URLs
    - Has Video: count of 'Y's in Video Upload
    - No Video: count of not 'Y's in Video Upload
    - % inv. w/ video: % of inventory with 'Y' in Video Upload. This will be coerced to a percent string later,
        but is needed for comparisons in add_columns()
    - % Inv w/ URLs: % of inventory with URLs. Not needed for any comparisons
    """
    df = pd.read_csv(csv_path)

    df["Valid V360"] = df["Video URL from Vendor"].apply(check_url_field, args=(False,))
    df["Blank/Invalid"] = df["Video URL from Vendor"].apply(check_url_field, args=(True,))
    df["Has Video"] = df["Video Upload"].apply(check_video_field, args=(False,))
    df["No Video"] = df["Video Upload"].apply(check_video_field, args=(True,))

    df.rename(columns={"Video Upload": "Total Inv", "Supplier": "Vendor"}, inplace=True)
    df = df[["Vendor", "Valid V360", "Blank/Invalid", "Has Video", "No Video", "Total Inv"]]
    df = df.groupby("Vendor", as_index=False).count()

    df["% inv. w/ video"] = ((df["Total Inv"] - df["Has Video"]) / df["Total Inv"]).round(4)
    df["% Inv w/ URLs"] = (100 - (df["Total Inv"] - df["Valid V360"]) / df["Total Inv"] * 100).round(2)
    df["% Inv w/ URLs"] = df["% Inv w/ URLs"].astype(str) + "%"

    return df


def add_comparison_columns(df: pd.DataFrame, new_data: dict) -> pd.DataFrame:
    """Add data from previous script runs for comparisons.

    new_df: expected to be in the form of {'VENDOR NAME': {'Prev Video': val, 'Prev Inven': val}}

    Prev Video: Dummy column name, contains the previous run's 'Has Video' value
    Prev Inven: Dummy column name, contains the previous run's 'Total Inv' value

    - NaN values for Prev Video/Inven are filled to current values to cause the comparison values to be 0. This is to
      handle new vendors being added
    """
    if new_data:  # should only be empty if new sheet
        new_df = pd.DataFrame.from_dict(new_data, orient="index")
        new_df.index.name = "Vendor"
        df = df.join(new_df, on="Vendor")

        df["Prev Video"] = df["Prev Video"].fillna(df["Has Video"])
        df["Prev Inven"] = df["Prev Inven"].fillna(df["% inv. w/ video"])

        df["Difference Since Last"] = df["Has Video"] - df["Prev Video"]

        df["Change in % inv. w/ video"] = ((df["% inv. w/ video"] - df["Prev Inven"]) * 100).round(2)
        df["Change in % inv. w/ video"] = df["Change in % inv. w/ video"].astype(str) + "%"
        df["% inv. w/ video"] = (df["% inv. w/ video"] * 100).round(2).astype(str) + "%"

        df.drop(["Prev Video", "Prev Inven"], axis="columns", inplace=True)

    return df
