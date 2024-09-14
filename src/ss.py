import smartsheet

from src.constants import SS_API_KEY


def get_dict_value(cols_dict: dict, col_name: str) -> int:
    """Return the columnId field based on the column name lookup."""
    col_id = cols_dict.get(col_name)
    if not col_id:
        raise ValueError(f"Column `{col_name}` is not present on this sheet.")
    return col_id


class SSheet:
    def __init__(self, api_key: str = None) -> None:
        self.parent_rows = {}
        self.previous_values = {}
        self.cols_dict = None
        self.sheet = None
        self.sheet_rows = []

        if not api_key:
            api_key = SS_API_KEY

        self.ss_client = smartsheet.Smartsheet(api_key)
        self.ss_client.errors_as_exceptions(True)
        self.base_row_vals = {"overrideValidation": True, "strict": False}

    def get_sheet(self, sheet_id: str | int) -> None:
        """Retrieve specified sheet, either by sheet name or sheet id."""

        def get_sheet_id(sheet_name: str) -> int:
            """Get the sheet id from the sheet name."""
            sheet_dict = self.ss_client.Sheets.list_sheets(include_all=True).to_dict()
            for sheet in sheet_dict["data"]:
                if sheet["name"].upper() == sheet_name.upper():
                    return sheet["id"]
            raise NameError("Cannot find the specified Smartsheet")

        if isinstance(sheet_id, str):
            sheet_id = get_sheet_id(sheet_id)
        elif not isinstance(sheet_id, int):
            raise TypeError("Value must either be the Sheet Name or Sheet ID.")

        self.sheet = self.ss_client.Sheets.get_sheet(sheet_id)
        self.sheet_rows = self.sheet.rows.to_list()
        self.get_dict_of_sheet_col_names()

    def get_dict_of_sheet_col_names(self) -> None:
        """Return dict of {col_title: col_id} for use in row generation.

        This is used to easily retrieve the columnId field by lookups on the column name.
        """
        col_dict = self.sheet.get_columns(include_all=True).to_dict()
        self.cols_dict = {i["title"]: i["id"] for i in col_dict["data"]}

    def get_parents_and_first_child_data(self, cell_cols: dict[str] = None) -> None:
        """Find all parent rows and update parent_rows attr. Optionally update previous_values attr.

        Parent Values:
          - create dict in the form of {PARENT_NAME: ROW_ID}

        Child Values:
          - create dict in the form of {PARENT_NAME: {COL_NAME: val}}

        This is used to easily retrieve the columnId field by lookups on the column names. The child values is used for
        adding additional rows to later uploads.
        """

        for i, row in enumerate(self.sheet.rows.to_list()):
            row = row.to_dict()

            # create parents dict
            if not row.get("parentId"):
                parent_name = row["cells"][0].get("value")
                if parent_name:  # helps handle empty rows
                    self.parent_rows.update({parent_name: row["id"]})
                    parent_index = i

            else:
                if cell_cols and i == parent_index + 1:  # most recent should be directly below parent, ie desc. order
                    self.get_values_from_row(row, cell_cols, parent_name)

    def get_values_from_row(self, row: smartsheet.models.Row, cell_cols: dict[str], parent_name: str) -> None:
        """Get values from the row specified by cell_cols data.

        cell_cols: This is a dict in the form of {'OUTPUT_COL_NAME', 'SS_COL_NAME'}
          - the OUTPUT_COL_NAME is used for the return value
          - the SS_COL_NAME matches against the sheet, and will be used to find the columnId (i.e. must match a SS col)
        """

        def find_cell_vals(row: smartsheet.models.Row, col_id: int) -> str:
            for cell in row["cells"]:
                if cell["columnId"] == col_id:
                    return cell.get("value", "")

        cells = {k: find_cell_vals(row, get_dict_value(self.cols_dict, v)) for k, v in cell_cols.items()}
        self.previous_values.update({parent_name: cells})

    def get_col_values_by_col_name(self, col_name: str) -> list[str]:
        """Return list of values in column given column name."""
        col_id = get_dict_value(self.cols_dict, col_name)
        return [cell.value for row in self.sheet.rows for cell in row.cells if cell.column_id == col_id]

    def add_row_single_col_single_val(self, col_name: str, value: str, update_parents: bool) -> None:
        """Add a new row with one value.

        col_name: column name for the single value. This will use self.cols_dict attr to find the columnId
        value: value to load in the new row under col_name
        update_parents: Optionally update self.parent_rows with the new rows
        """
        col_id = get_dict_value(self.cols_dict, col_name)
        row = self.ss_client.models.Row({"cells": [{"column_id": col_id, "value": value, **self.base_row_vals}]})
        new_row = self.sheet.add_rows(row)

        if update_parents:
            self.parent_rows.update({value: new_row.to_dict()["result"][0]["id"]})

    def add_child_rows(self, row_data: list[dict], parent_row: str) -> None:
        """Add a child row to the sheet. API does not allow rows with differing parentIds to be
        added in same request.

        - Updates the cell list using the row_data passed to method
        - assumes toTop
        - Column names from DF and from SS must match (will throw exception if not)
        """
        cells = [
            {
                "column_id": get_dict_value(self.cols_dict, col["col_name"]),
                "value": col["value"],
                **self.base_row_vals,
            }
            for col in row_data
        ]
        new_row = self.ss_client.models.Row({"parentId": self.parent_rows[parent_row], "toTop": True, "cells": cells})
        self.sheet.add_rows([new_row])

    def upload_dataframe(self, df: "pd.DataFrame") -> None:
        """Convert a DF to Smartsheet in bulk.

        Does not work for parent/child rows.
        """
        new_rows = []
        for row in df.iterrows():
            cells = [
                {
                    "column_id": get_dict_value(self.cols_dict, col),
                    "value": val,
                    "displayValue": str(val),
                    **self.base_row_vals,
                }
                for col, val in row[1].items()
            ]
            new_rows.append(self.ss_client.models.Row({"toBottom": True, "cells": cells}))

        # issues with posting if over a certain size
        chunk_len = 100000  # somewhat aribitrary, tested with length of ~200000 so this is conservative
        if len(new_rows) > chunk_len:
            chunks = new_rows // chunk_len + 1  # add one to account for remainder
            new_list = [new_rows[i:i + chunks] for i in range(0, len(new_rows), chunks)]
            for sub_list in new_list:
                self.sheet.add_rows(sub_list)
        else:
            self.sheet.add_rows(new_rows)
