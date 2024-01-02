import asyncio
import logging
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.validation import Function
from textual.widgets import Button, Footer, Header, Input, Label, Rule

from src import data, ss, utils
from src.constants import *
from src.screens import Browser, ErrApp, Output, Waiting

LOG_DIR = Path("logs/")
if not LOG_DIR.exists():
    LOG_DIR.mkdir()

logging.basicConfig(filename=f"logs/{utils.TODAY}.log", filemode="w")


class MainApp(App):
    CSS_PATH = "src/gui.tcss"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
    ]
    ENABLE_COMMAND_PALETTE = False

    ss_name = utils.load_constants()["sheet"]
    csv = reactive(utils.get_latest_csv())
    date = reactive(utils.TODAY)
    ssheet = None
    df = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Smartsheet Name")
        yield Input(id="sheet", value=self.ss_name, placeholder="Enter the smartsheet to upload to...")

        yield Rule(line_style="heavy")

        yield Label("CSV to Upload. Defaults to most recent CSV.")
        yield Input(
            id="file",
            value="",
            placeholder="Enter the latest CSV file...",
            validators=[Function(utils.is_valid_file, "Not a valid file.")],
            classes="validinput",
        )
        yield Label(id="file_label")
        with Horizontal():
            yield Button("Get Recent", id="recent", variant="default")
            yield Button("Browse", id="browse", variant="primary")

        yield Rule(line_style="heavy")

        yield Label("Date for the upload.")
        yield Input(
            id="date",
            placeholder="Enter date for upload...",
            validators=[Function(utils.is_valid_date, "Not a valid date.")],
            classes="validinput",
        )
        yield Label(id="date_label")
        yield Button("Today", id="today", variant="default")

        yield Rule(line_style="heavy")

        with Horizontal():
            yield Button("Submit", id="submit", variant="success")
            yield Button("Exit", id="exit", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self.title = UI_TITLE
        self.query_one("#file").focus()

    @on(Input.Changed, "#validinput")
    def show_invalid_reasons(self, event: Input.Changed) -> None:
        """Updates the UI to show the reasons why validation failed."""

        def update_label(control: str, msg: str) -> None:
            self.query_one(f"#{control.id}_label").update(msg)

        if not event.validation_result.is_valid:
            update_label(event.control, event.validation_result.failure_descriptions[0])
        else:
            update_label(event.control, "Valid")

    @on(Button.Pressed, "#submit")
    def submit(self) -> None:
        file = self.query_one("#file")
        date = self.query_one("#date")
        if all((file.value, date.value)) and all((file.is_valid, date.is_valid)):
            self.csv = utils.INPUTS_DIR + file.value
            self.date = date.value
            self.ss_name = self.query_one("#sheet").value
            self.main()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        def file_input(val: Path) -> None:
            if val:
                self.query_one("#file").value = val.name

        match event.button.id:
            case "recent":
                self.query_one("#file").value = self.csv
            case "browse":
                self.push_screen(Browser(), file_input)
            case "today":
                self.query_one("#date").value = self.date
            case "exit":
                self.app.exit()

    @work
    async def main(self) -> None:
        """Main function to process data.

        - creates the DataFrame and initializes smartsheets
        - get initial data from SS needed for processing the comparison data
            - these are values that are being compared to the current data using data from the smartsheet
            - i.e. previous uploads
        - upload all new vendors (i.e. not present on smartsheet)
        - update DF with comparison data
        - update smartsheet

        All exceptions are sent to log, and the app is exited with return_code 4 to trigger the error app.
        """
        try:
            await self.push_screen(Waiting())

            await asyncio.gather(self.get_df(), self.get_ss())
            self.ssheet.get_parents_and_first_child_data({"Prev Video": SS_VIDEO_TRUE, "Prev Inven": SS_PERC_INV})
            new_vendors = self.load_new_vendors()
            self.df = data.add_comparison_columns(self.df, self.ssheet.previous_values)
            self.update_smartsheet()

            self.pop_screen()
            await self.push_screen(Output(utils.create_markdown(new_vendors, self.date)))

            utils.update_csv_isoformat(self.csv)
            utils.save_constants({"sheet": self.ss_name})

        except Exception as err:
            logging.exception(err, exc_info=True, stack_info=True)
            self.exit(return_code=4, message=err)

    async def get_df(self) -> None:
        """Initialize dataframe."""
        self.df = data.create_output_df(self.csv)

    async def get_ss(self) -> None:
        """Initialize smartsheet."""
        self.ssheet = ss.SSheet()
        self.ssheet.get_sheet(self.ss_name)

    def load_new_vendors(self) -> list:
        """Push new vendors to the sheet."""
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

        - Values in the first column are expected to be a date
        - Even though the first column is dates, new rows are simply added as the first child row under that parent.
        - Creates row_vals for the row, which are a list of cells. Each cell element will have the column_name and
          value fields
        - This is sent to the smartsheet method along with the parent name, i.e. the Vendor (df_row[0])
        """
        df_cols = list(self.df.columns)
        for _, df_row in self.df.iterrows():
            row_vals = []
            for i, col in enumerate(df_cols):
                val = self.date if i == 0 else df_row[i]
                row_vals.append({"col_name": col, "value": val})

            self.ssheet.add_child_rows(row_vals, df_row[0])


app = MainApp()

if __name__ == "__main__":
    a = app.run()
    if app.return_code == 4:
        ErrApp().run()
