from typing import Final

# UI Title
UI_TITLE: Final = "Diamonds Program"

# Column names on Smartsheet
SS_VENDOR: Final = "Vendor"
SS_VALID_URLS: Final = "Valid V360"
SS_BLANK_URLS: Final = "Blank/Invalid"
SS_VIDEO_TRUE: Final = "Has Video"
SS_VIDEO_FALSE: Final = "No Video"
SS_VIDEO_INV: Final = "Total Inv"
SS_PERC_INV: Final = "% inv. w/ video"
SS_PERC_INV_URL: Final = "% Inv w/ URLs"
SS_INV_DELTA: Final = "Difference Since Last"
SS_VID_INV_DELTA: Final = "Change in % inv. w/ video"
SS_DATE: Final = "Date"

# Column names on CSV
CSV_VENDOR: Final = "Supplier"
CSV_URL: Final = "Video URL from Vendor"
CSV_VIDEO: Final = "Video Upload"

# values to check for in URLs
URL_TEST_STRINGS: Final = [
    "diacam",
    "mp4",
    "gem360",
]
