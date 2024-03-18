import pandas as pd
import validators

from src.constants import *


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

    test = not (any(i in url for i in URL_TEST_STRINGS) or len(url) < 6)
    return bool_fields_test(test, reverse)


def create_output_df(df: pd.DataFrame, date: str) -> pd.DataFrame:
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

    def check_type_field(type_val: str | None) -> str:
        """Check the CSV_TYPE field and coerce to correct value."""
        if "lab" in type_val.lower():
            return "Lab"
        elif type_val:
            return "Natural"
        return ""

    # df = pd.read_csv(csv_path)

    df[SS_VALID_URLS] = df[CSV_URL].apply(check_url_field, args=(False,))
    df[SS_BLANK_URLS] = df[CSV_URL].apply(check_url_field, args=(True,))
    df[SS_VIDEO_TRUE] = df[CSV_VIDEO].apply(check_video_field, args=(False,))
    df[SS_VIDEO_FALSE] = df[CSV_VIDEO].apply(check_video_field, args=(True,))

    df_type = df[[CSV_VENDOR, CSV_TYPE]].drop_duplicates(CSV_VENDOR)
    df = df[[CSV_VENDOR, SS_VALID_URLS, SS_BLANK_URLS, SS_VIDEO_TRUE, SS_VIDEO_FALSE, CSV_VIDEO]]

    df = df.groupby(CSV_VENDOR, as_index=False).count()
    df = pd.merge(df, df_type, on=CSV_VENDOR)
    df[SS_DATE] = date
    df[CSV_TYPE] = df[CSV_TYPE].apply(lambda x: check_type_field(x))

    df.rename(columns={CSV_VIDEO: SS_VIDEO_INV, CSV_VENDOR: SS_VENDOR, CSV_TYPE: SS_TYPE}, inplace=True)

    df[SS_PERC_INV] = 1 - ((df[SS_VIDEO_INV] - df[SS_VIDEO_TRUE]) / df[SS_VIDEO_INV])
    df[SS_PERC_INV_URL] = (100 - ((df[SS_VIDEO_INV] - df[SS_VALID_URLS]) / df[SS_VIDEO_INV] * 100)).round(2)
    df[SS_PERC_INV_URL] = df[SS_PERC_INV_URL].astype(str) + "%"

    return df


def add_comparison_columns(df: pd.DataFrame, new_data: dict) -> pd.DataFrame:
    """Add data from previous script runs for comparisons.

    new_data: expected to be in the form of {'VENDOR NAME': {'Prev Video': val, 'Prev Inven': val}}

    Prev Video: Dummy column name, contains the previous run's 'Has Video' value
    Prev Inven: Dummy column name, contains the previous run's 'Total Inv' value

    - NaN values for Prev Video/Inven are filled to current values to cause the comparison values to be 0. This is to
      handle new vendors being added
    """
    if new_data:  # should only be empty if new sheet
        new_df = pd.DataFrame.from_dict(new_data, orient="index")
        new_df.index.name = SS_VENDOR
        df = df.join(new_df, on=SS_VENDOR)

        df["Prev Video"] = df["Prev Video"].fillna(df[SS_VIDEO_TRUE])
        df["Prev Inven"] = df["Prev Inven"].fillna(df[SS_PERC_INV])

        # inputs from SS are str with %
        # raises AttributeError if the cells are not in percent format. Click the percent icon in SS to fix this
        df[SS_INV_DELTA] = df[SS_VIDEO_TRUE] - df["Prev Video"]
        if df["Prev Inven"].dtype == str:
            df["Prev Inven"] = df["Prev Inven"].str.rstrip("%").astype("float") / 100.0

        df[SS_VID_INV_DELTA] = ((df[SS_PERC_INV] - df["Prev Inven"]) * 100).round(2)
        df[SS_VID_INV_DELTA] = df[SS_VID_INV_DELTA].astype(str) + "%"
        df[SS_PERC_INV] = (df[SS_PERC_INV] * 100).round(2).astype(str) + "%"

        df.drop(["Prev Video", "Prev Inven"], axis="columns", inplace=True)

    return df
