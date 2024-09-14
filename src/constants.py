from typing import Final

# UI Title
UI_TITLE: Final[str] = "Diamonds Program"

SS_API_KEY: Final[str] = "FF8W4twmkyxslTkWRqLabgnI0odHKPhUk5V7S"

# Name of the Smartsheet, exact match
COVERAGES_SHEET_NAME: Final[str] = "Diamond Video Coverage Tracker 2024"
AUDIT_SHEET_NAME: Final[str] = "Colorless Diamond Audit"

# Column names on Smartsheet
# Note: Adding columns will have no effect on the output. This is only for name changes
SS_VENDOR: Final[str] = "Vendor"
SS_VIDEO_LINK: Final[str] = "Video Link"
SS_VALID_URLS: Final[str] = "Valid V360"
SS_BLANK_URLS: Final[str] = "Blank/Invalid"
SS_VIDEO_TRUE: Final[str] = "Has Video"
SS_VIDEO_FALSE: Final[str] = "No Video"
SS_VIDEO_INV: Final[str] = "Total Inv"
SS_PERC_INV: Final[str] = "% inv. w/ video"
SS_PERC_INV_URL: Final[str] = "% Inv w/ URLs"
SS_INV_DELTA: Final[str] = "Difference Since Last"
SS_VID_INV_DELTA: Final[str] = "Change in % inv. w/ video"
SS_DATE: Final[str] = "Date"
SS_TYPE: Final[str] = "Type"
SS_STOCK: Final[str] = "Stock Number"
SS_CERT: Final[str] = "Cert Number"

# Column names on CSV
CSV_VENDOR: Final[str] = "Supplier"
CSV_URL: Final[str] = "Video URL from Vendor"
CSV_VIDEO: Final[str] = "Video Upload"
CSV_TYPE: Final[str] = "Cert of Origin"
CSV_STOCK: Final[str] = "Stock #"
CSV_CERT: Final[str] = "CertNumber"

# values to check for in URLs
URL_TEST_STRINGS: Final[list[str]] = [
    "diacam",
    "mp4",
    "gem360",
]
