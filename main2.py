"""
For each vendor:
•	Count number of valid useable links in column “Video URL from Vendor” -> 'Valid V360'
•	Count number of invalid links or blank cells in column “Video URL from Vendor” -> 'Blank/Invalid'
•	Count number of “Y” in column “Video Upload” -> 'Has Video'
•	Count number of “N” in column “Video Upload” -> 'No Video'
•	Sum last two actions -> 'Total Inv'


for url checking: https://stackoverflow.com/questions/72013184/how-to-request-data-from-hundreds-of-urls-in-python

---

How to determine if URL is valid: =OR(ISNUMBER(SEARCH("diacam",Video URL from Vendor@row)),ISNUMBER(SEARCH("mp4", Video URL from Vendor@row)),ISNUMBER(SEARCH("gem360", Video URL from Vendor@row)),LEN(Video URL from Vendor@row)<6)

In summary, the formula returns TRUE if any of the following conditions are met:
    - The text "diacam" is found in Video URL from Vendor@row.
    - The text "mp4" is found in Video URL from Vendor@row.
    - The text "gem360" is found in Video URL from Vendor@row.
    - The text in Video URL from Vendor@row is less than 6 characters long.

If none of these conditions are met, the formula returns FALSE.

- For each vendor, the number of FALSE will be calculated into Valid V360 on Pivot
- For each vendor, the number of TRUE will be calculated into Blank/Invalid on Pivot
- For any values not returning either true or false, example: #VALUE!, calculate these in the #VALUE! column

- Count number of “Y” in column “Video Upload” and calculate into Has Video on Pivot
- Count number of “N” in column “Video Upload” and calculate into No Video on Pivot
- Sum last two actions and calculate into Total Inv Column
- *If vendor does not exist, add to URL Status sheet

- needs to have the user
 


"""
a = ["Finestar", "Mehta Dubai", "Palak India", "SRK Dubai"]

from pathlib import Path
from typing import Final, Iterable

from pytz import timezone

from src import data, ss

TIMEZONE: Final = "US/Pacific"
INPUTS_DIR: Final = "INPUTS/"

MONTHS: Final = ("JAN", "FEB", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUG", "SEP", "OCT", "NOV", "DEC")

SHEET_NAME = "Count of URL Status 2024"
SHEET_ID = (6123703112781700,)


def get_file_path(filename: str) -> Path:
    file_path = Path(filename)
    if file_path.is_file():
        return file_path
    raise FileNotFoundError(f"{filename} cannot be found.")


def filter_list(_list: list, filter_list: Iterable) -> list:
    return [i for i in _list if i not in filter_list]


def add_new_vendors(ssheet, vendors: list[str]):
    for vendor in vendors:
        ssheet.add_row_to_sheet(vendor)
        for month in MONTHS:
            ssheet.add_row_to_sheet(month)


def main():
    # Replit server is UTC
    tz = timezone(TIMEZONE)

    filename = "INPUTS/Diamond_Video_Cert_Status_12423.csv"
    csv_file = get_file_path(filename)

    api_key = retrieve_token()
    ssheet = ss.SSheet(api_key)
    ssheet.get_sheet(SHEET_NAME)
    vendors_raw = ssheet.get_col_values_by_col_name("Vendor")
    vendors = filter_list(vendors_raw, MONTHS)

    # output_table = data.create_output_df(csv_file)
    # new_vendors = filter_list(output_table["Supplier"], vendors)

    # vendors = ss.VENDORS
    suppliers = data.SUPPLIERS
    new_vendors = filter_list(suppliers, vendors)
    # print(new_vendors)

    for vendor in new_vendors:
        ssheet.add_single_col_nested_row_to_sheet("Vendor", vendor, MONTHS)

    INPUT_MONTH = "AUG"


if __name__ == "__main__":
    gui.app.run()

    main()

# vendor_id = 5572694083850116
# valid_v360 = 3320894270164868
# rows = [
#     {"column_id": vendor_id},
#     {"column_id": vendor_id},
# ]
# a = {
#     "accessLevel": "OWNER",
#     "cells": [
#         {"columnId": 5572694083850116, "displayValue": "Aspeco", "value": "Aspeco"},
#         {"columnId": 3320894270164868},
#         {"columnId": 7824493897535364},
#         {"columnId": 2194994363322244},
#         {"columnId": 8950393804377988},
#         {"columnId": 48747665903492},
#         {
#             "columnId": 4552347293273988,
#             "displayValue": "0",
#             "formula": '=IFERROR([No Video]@row + [Has Video]@row, " ")',
#             "value": 0.0,
#         },
#     ],
#     "createdAt": "2023-12-12T21:56:55+00:00Z",
#     "expanded": False,
#     "id": 6469573455417220,
#     "modifiedAt": "2023-12-29T21:48:03+00:00Z",
#     "rowNumber": 1,
#     "sheetId": 6123703112781700,
#     "version": 21,
# }
# a = sheet.add_rows(
#     [
#         {
#             "toTop": True,
#             "cells": [
#                 {
#                     "column_id": vendor_id,
#                     "displayValue": "TEST1234",
#                     "value": "TEST1234",
#                     "overrideValidation": True,
#                     "strict": False,
#                 },
#                 {"column_id": 3320894270164868, "value": "TEST123456", "overrideValidation": True, "strict": False},
#             ],
#         }
#     ]
# )
# a.message
#
# row.to_top = True
#
# row = ss_client.models.Row({"parentId": 8896508249565060, "toBottom": True})
#
# row.cells.append({"column_id": vendor_id, "value": "TEST1234", "overrideValidation": True, "strict": False})
# sheet.add_rows([row])
#
# {
#     "cells": [
#         {"columnId": 5572694083850116, "displayValue": "JAN", "value": "JAN"},
#         {"columnId": 3320894270164868},
#         {"columnId": 7824493897535364},
#         {"columnId": 2194994363322244},
#         {"columnId": 8950393804377988},
#         {"columnId": 48747665903492},
#         {
#             "columnId": 4552347293273988,
#             "displayValue": "0",
#             "formula": '=IFERROR([No Video]@row + [Has Video]@row, " ")',
#             "value": 0.0,
#         },
#     ],
#     "createdAt": "2023-12-12T21:56:55+00:00Z",
#     "expanded": True,
#     "id": 7390964199493508,
#     "modifiedAt": "2023-12-12T23:55:57+00:00Z",
#     "parentId": 6469573455417220,
#     "rowNumber": 2,
# }

x = {
    "data": [
        {
            "cells": [
                {"columnId": 251946159001476, "displayValue": "Amipi Natural", "value": "Amipi Natural"},
                {"columnId": 6546146643103620},
                {"columnId": 4294346829418372},
                {"columnId": 6884200297746308},
                {"columnId": 4755545786371972},
                {"columnId": 2503745972686724},
                {"columnId": 1377846065844100},
                {"columnId": 5881445693214596},
                {"columnId": 8797946456788868},
                {
                    "columnId": 3629645879529348,
                    "displayValue": "0",
                    "formula": '=IFERROR([No Video]@row + [Has Video]@row, " ")',
                    "value": 0.0,
                },
                {"columnId": 212959667113860},
                {"columnId": 4716559294484356},
                {"columnId": 2464759480799108},
                {"columnId": 1254700763533188},
                {"columnId": 5758300390903684},
                {"columnId": 3506500577218436},
                {"columnId": 8010100204588932},
            ],
            "createdAt": "2023-12-31T04:10:22+00:00Z",
            "expanded": True,
            "id": 6271143668780932,
            "modifiedAt": "2023-12-31T04:10:22+00:00Z",
            "rowNumber": 3,
            "sheetId": 340099346681732,
            "siblingId": 4687150871646084,
        }
    ],
    "message": "SUCCESS",
    "result": [
        {
            "cells": [
                {"columnId": 251946159001476, "displayValue": "Amipi Natural", "value": "Amipi Natural"},
                {"columnId": 6546146643103620},
                {"columnId": 4294346829418372},
                {"columnId": 6884200297746308},
                {"columnId": 4755545786371972},
                {"columnId": 2503745972686724},
                {"columnId": 1377846065844100},
                {"columnId": 5881445693214596},
                {"columnId": 8797946456788868},
                {
                    "columnId": 3629645879529348,
                    "displayValue": "0",
                    "formula": '=IFERROR([No Video]@row + [Has Video]@row, " ")',
                    "value": 0.0,
                },
                {"columnId": 212959667113860},
                {"columnId": 4716559294484356},
                {"columnId": 2464759480799108},
                {"columnId": 1254700763533188},
                {"columnId": 5758300390903684},
                {"columnId": 3506500577218436},
                {"columnId": 8010100204588932},
            ],
            "createdAt": "2023-12-31T04:10:22+00:00Z",
            "expanded": True,
            "id": 6271143668780932,
            "modifiedAt": "2023-12-31T04:10:22+00:00Z",
            "rowNumber": 3,
            "sheetId": 340099346681732,
            "siblingId": 4687150871646084,
        }
    ],
    "resultCode": 0,
    "version": 199,
}
