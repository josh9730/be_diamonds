import time

import pandas as pd

from src import data, ss, utils
from src.constants import *


class Main:
    def __init__(self):
        self.ssheet: ss.SSheet = None
        self.df: pd.DataFrame = None

        self.input_df: pd.DataFrame = None
        self.date: str = None
        self.ss_name: str = None

        # used for value bindings for the Vendor Audits, see vendors_page() for details
        self.selected_vendors: dict[str, bool] = {}

    def csv_vendors(self):
        if self.input_df is not None:
            all_vendors = self.input_df[CSV_VENDOR].unique().tolist()

            # expected to be pruned
            try:
                all_vendors.pop(all_vendors.index("BE Internal"))
            except ValueError:
                ...

        else:
            all_vendors = []
        if all_vendors:
            self.selected_vendors = {i: False for i in all_vendors}

    def run_both(self):
        self.run_coverages()
        self.run_audits()

    def run_coverages(self):
        self.get_df()
        self.get_ss()
        self.ssheet.get_parents_and_first_child_data({"Prev Video": SS_VIDEO_TRUE, "Prev Inven": SS_PERC_INV})
        new_vendors = self.load_new_vendors()
        self.df = data.add_comparison_columns(self.df, self.ssheet.previous_values)

        if len(new_vendors) > 5:
            time.sleep(10)
        self.update_smartsheet()

        utils.save_sheet_name(ss_name, "coverages")

    def run_audits(self):
        ...

    def get_df(self):
        self.df = data.create_output_df(self.input_df, self.date)

    def get_ss(self):
        self.ssheet = ss.SSheet()
        self.ssheet.get_sheet(self.ss_name)

    def load_new_vendors(self) -> list[str | None]:
        """Push new vendors to the sheet.

        Returns a list of vendors or empty list
        """
        ss_vendors = list(self.ssheet.parent_rows.keys())
        new_vendors = utils.filter_list(self.df[SS_VENDOR], ss_vendors)
        if new_vendors:
            for vendor_val in new_vendors:
                self.ssheet.add_row_single_col_single_val(SS_VENDOR, vendor_val, update_parents=True)
            return new_vendors
        return []

    def update_smartsheet(self) -> None:
        """Iterates over DataFrame and uploads by row by row. API does not allow rows with differing parentIds to be
        added in same request.

        - New rows are simply added as the first child row under that parent.
        - Creates row_vals for the row, which are a list of cells. Each cell element will have the column_name and
          value fields
        - This is sent to the smartsheet method along with the parent name, i.e. the Vendor (df_row[0])
        """
        df_cols = list(self.df.columns)
        for _, df_row in self.df.iterrows():
            row_vals = []
            for i, col in enumerate(df_cols):
                row_vals.append({"col_name": col, "value": df_row[i]})

            self.ssheet.add_child_rows(row_vals, df_row[0])
