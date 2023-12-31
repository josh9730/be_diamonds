import smartsheet


def get_dict_value(cols_dict: dict, col_name: str) -> int:
    col_id = cols_dict.get(col_name)
    if not col_id:
        raise ValueError(f"Column `{col_name}` is not present on this sheet.")
    return col_id


def filter_list_of_rows(rows: list):
    """Return dict of {NAME: ID}."""
    parent_rows = {}
    for row in rows:
        row = row.to_dict()
        if not row.get("parentId"):
            parent_rows.update({row["cells"][0]["value"]: row["id"]})
    return parent_rows


class SSheet:
    def __init__(self, api_key: str) -> None:
        self.parent_rows = None
        self.cols_dict = None
        self.sheet = None

        self.ss_client = smartsheet.Smartsheet(api_key)
        self.ss_client.errors_as_exceptions(True)

        self.base_row_vals = {"overrideValidation": True, "strict": False}

    def get_sheet(self, sheet: str | int) -> None:
        def get_sheet_id(sheet_name: str) -> int:
            sheet_dict = self.ss_client.Sheets.list_sheets(include_all=True).to_dict()
            for sheet in sheet_dict["data"]:
                if sheet["name"].upper() == sheet_name.upper():
                    return sheet["id"]
            raise NameError("Cannot find the specified Smartsheet")

        if isinstance(sheet, str):
            sheet_id = get_sheet_id(sheet)
        elif not isinstance(sheet, int):
            raise TypeError("Value must either be the Sheet Name or Sheet ID.")

        self.sheet = self.ss_client.Sheets.get_sheet(sheet_id)
        self._get_dict_of_sheet_col_names()

    def _get_dict_of_sheet_col_names(self) -> None:
        """Return dict of {col_title: col_id} for use in row generation"""
        col_dict = self.sheet.get_columns(include_all=True).to_dict()
        self.cols_dict = {i["title"]: i["id"] for i in col_dict["data"]}

    def get_parents_first_column(self):
        """Return dict of parents in first column, {row value: row_id}."""
        rows_list = self.sheet.rows.to_list()
        self.parent_rows = filter_list_of_rows(rows_list)

    def get_col_values_by_col_name(self, col_name: str) -> list[str]:
        """Return list of values in column given column name."""
        col_id = get_dict_value(self.cols_dict, col_name)
        return [cell.value for row in self.sheet.rows for cell in row.cells if cell.column_id == col_id]

    def add_new_row_first_col(self, col_name: str, value: str, update_parents: bool) -> None:
        col_id = get_dict_value(self.cols_dict, col_name)
        row = self.ss_client.models.Row({"cells": [{"column_id": col_id, "value": value, **self.base_row_vals}]})
        new_row = self.sheet.add_rows(row)
        if update_parents:
            self.parent_rows.update({value: new_row.to_dict()["result"][0]["id"]})

    def add_child_rows_to_sheet(self, df, date):
        """Rows added singly, API does not allow rows with differing parentIds to be added in same request."""
        df_cols = list(df.columns)
        for index, df_row in df.iterrows():
            cells = []
            for i, col in enumerate(df_cols):
                if i == 0:
                    val = date
                else:
                    val = df_row[i]
                cells.append({"column_id": get_dict_value(self.cols_dict, col), "value": val, **self.base_row_vals})

            new_row = self.ss_client.models.Row(
                {"parentId": self.parent_rows[df_row[0]], "toBottom": True, "cells": cells}
            )
            self.sheet.add_rows([new_row])
