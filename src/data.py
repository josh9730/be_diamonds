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
    df = pd.read_csv(csv_path)

    df["Valid V360"] = df["Video URL from Vendor"].apply(check_url_field, args=(False,))
    df["Blank/Invalid"] = df["Video URL from Vendor"].apply(check_url_field, args=(True,))
    df["Has Video"] = df["Video Upload"].apply(check_video_field, args=(False,))
    df["No Video"] = df["Video Upload"].apply(check_video_field, args=(True,))

    df.rename(columns={"Video Upload": "Total Inv", "Supplier": "Vendor"}, inplace=True)
    df = df[["Vendor", "Valid V360", "Blank/Invalid", "Has Video", "No Video", "Total Inv"]]

    return df.groupby("Vendor", as_index=False).count()
