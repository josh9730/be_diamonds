import time

import pandas as pd

from src import data, ss, utils
from src.constants import *


class Main:
    """Main class for the various functions perfomed by this tool.

    Also used for data persistence scross UI functions, esp. for binding purposes (i.e. dataclass)
    Wraps the data and ss modules for use by the UI.
    """

    def __init__(self):
        self.ssheet_cov: ss.SSheet = None
        self.ssheet_audit: ss.SSheet = None
        self.coverages_sheet_name: str = None
        self.audit_sheet_name: str = None

        self.coverage_df: pd.DataFrame = None
        self.audit_df: pd.DataFrame = None
        self.input_df: pd.DataFrame = None
        self.date: str = None
        self.audit_num: int = None
        self.selected_vendors: dict[str, bool] = {}

    def csv_vendors(self):
        """Populate selected_vendors, used for vendor bindings."""
        if self.input_df is not None:
            all_vendors = self.input_df[CSV_VENDOR].unique().tolist()
            try:
                all_vendors.pop(all_vendors.index("BE Internal"))
            except ValueError:
                ...
        else:  # default value for initial page creation
            all_vendors = []
        if all_vendors:
            self.selected_vendors = {i: False for i in all_vendors}

    def create_vendors_list(self) -> list[str]:
        """Return list of vendors with values of True."""
        return [k for k, v in self.selected_vendors.items() if v]

    def run_both(self):
        self.run_coverages()
        self.run_audits()

    def run_coverages(self):
        """Run methods to add to Diamond Coverages sheet."""
        self.get_coverages_ss()
        self.coverage_df = data.create_output_df(self.input_df, self.date)
        self.ssheet_cov.get_parents_and_first_child_data({"Prev Video": SS_VIDEO_TRUE, "Prev Inven": SS_PERC_INV})
        new_vendors = self.load_new_vendors()
        self.coverage_df = data.add_comparison_columns(self.coverage_df, self.ssheet_cov.previous_values)

        if len(new_vendors) > 5:  # seems to help with API when uploading many vendors
            time.sleep(10)
        self.iterate_and_load_rows()

    def run_audits(self):
        """Run methods to add to Vendor Audit sheet."""
        self.get_audit_ss()
        self.audit_df = data.parse_vendor_audit(self.input_df, self.create_vendors_list(), self.date, self.audit_num)
        utils.save_df_output(self.audit_df)
        self.ssheet_audit.upload_dataframe(self.audit_df)

    def get_coverages_ss(self):
        self.ssheet_cov = ss.SSheet()
        self.ssheet_cov.get_sheet(self.coverages_sheet_name)

    def get_audit_ss(self):
        self.ssheet_audit = ss.SSheet()
        self.ssheet_audit.get_sheet(self.audit_sheet_name)

    def load_new_vendors(self) -> list[str | None]:
        """Push new vendors to the sheet.

        Returns a list of vendors or empty list
        """
        ss_vendors = list(self.ssheet_cov.parent_rows.keys())
        new_vendors = utils.filter_list(self.coverage_df[SS_VENDOR], ss_vendors)
        if new_vendors:
            for vendor_val in new_vendors:
                self.ssheet_cov.add_row_single_col_single_val(SS_VENDOR, vendor_val, update_parents=True)
            return new_vendors
        return []

    def iterate_and_load_rows(self) -> None:
        """Iterates over DataFrame and uploads by row by row. API does not allow rows with differing parentIds to be
        added in same request.

        - New rows are simply added as the first child row under that parent.
        - Creates row_vals for the row, which are a list of cells. Each cell element will have the column_name and
          value fields
        - This is sent to the smartsheet method along with the parent name, i.e. the Vendor (df_row[0])
        """
        df_cols = list(self.coverage_df.columns)
        for _, df_row in self.coverage_df.iterrows():
            row_vals = []
            for i, col in enumerate(df_cols):
                row_vals.append({"col_name": col, "value": df_row[i]})

            self.ssheet_cov.add_child_rows(row_vals, df_row[0])
