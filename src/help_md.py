from src.constants import *

main_help = f"""#### Program Description
This program accepts a CSV input, parses, and uploads to Smartsheet.

###### CSV Fields
*NOTE*: This program must be able to handle the CSV and Smartsheet column names *and* data types in the Smartsheet columns. 
Most problems are due to changes, intentional or otherwise, to the column names or to the Smartsheet data types (e.g. a percent field and a number field are different).

##### Issue Reporting
Please direct all issues and questions to Mickey Avila (mickey.avila@brilliantearth.com).

---

##### Main Page
1. A CSV is required to move to the next step. Drag and drop the new CSV file to the box
2. Select the Action option:
  - Coverages: launch the Coverage script
  - Vendor Audit: launch the Vendor Audit script
  - Coverages & Audit: launch both (Coverages is run first)  

##### Coverages Script
1. A CSV input file is uploaded
2. Next, inputs for the Smartsheet name and upload date are gathered
3. The script will parse the CSV file (via `Pandas`, i.e. excel for Python) using the following algorithm:
  - The *{CSV_URL}* column is checked for valid URLs
  - The *{CSV_VIDEO}* column is checked for "Y" values (blank or other values are assumed to be "N")
  - Unneccessary columns are dropped, and the data is summed/grouped by *{CSV_VENDOR}*
  - The *{CSV_TYPE}* field is parsed:
    - If 'lab' in the value, coerce to 'Lab'
    - If the value is something other than 'lab', coerce to 'Natural'
    - Otherwise, return an empty string
  - Apply the selected date to all rows in the data
  - CSV Column names are coerced to match the appropriate Smartsheet column names
    - i.e. the *{CSV_VENDOR}* name from the CSV input is renamed to *{SS_VENDOR}*
  - Computed values are calculated:
    - *{SS_PERC_INV}*, by evaluating how many items have a "Y" in the *{CSV_VIDEO}* column
    - *{SS_PERC_INV_URL}*, by evaluating how many items have valid URLs
4. Any new vendors are loaded to Smartsheets as 'parent' rows 
5. Next, the script will retrieve values from Smartsheet for comparison to the previous script uploads:
  - The main assumption made is that the first (from the top) child row for each vendor is the most recent
  - *{SS_INV_DELTA}* and *{SS_VID_INV_DELTA}* are calcuated using the new values compared to the previous iteration's data from Smartsheet
6. Finally, all of the new data is loaded to Smartsheet. Each vendor's new row is loaded as a 'child' row, immediately below the parent
  - Note: Because of the parent/child rows being used, the data must be loaded row-by-row (Smartsheet limitation) and is therefore not very performant

##### Vendor Audit Script
1. A CSV input file is uploaded
2. Next, inputs for the Smartsheet name and upload date are gathered
3. The audit options are selected:
  - Weekly Audit (10 stock) or Deep Dive (1000 stock)
    - A manual number of stock may be input if needed
  - Vendors to audit
    - The list of vendors is populated from the CSV
    - Select the vendors to audit, or selected 'Audit All Vendors' to select all
4. The script will parse the CSV file using the following algorithm:
  - Filter out all items that do not have a 'Y' in the *{CSV_VIDEO}* column
  - Drop unneeded columns
  - For each selected vendor, sort by the *{CSV_STOCK}* column, and return the most recent X items, where X is the audit number selected
  - Apply the selected date to all rows in the data
  - CSV Column names are coerced to match the appropriate Smartsheet column names
    - i.e. the *{CSV_VENDOR}* name from the CSV input is renamed to *{SS_VENDOR}*
5. The data will be uploaded (in bulk, since there are no parent/child rows) to Smartsheet
"""
