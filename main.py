import asyncio
from datetime import datetime
from pathlib import Path
from typing import Final

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.validation import Function
from textual.widgets import Button, DirectoryTree, Footer, Header, Input, Label, Markdown, Rule

from src import utils, data, ss

TODAY: Final = datetime.today().strftime("%Y-%m-%d")
INPUTS_DIR: Final = "INPUTS/"


class Output(Screen):
    def __init__(self, output: str) -> None:
        self.output = output
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Markdown(self.output)
        yield Button("Finish", id="exit", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.exit()


class Waiting(ModalScreen):
    class Change(Message):
        def __init__(self) -> None:
            super().__init__()

    def on_waiting_change(self):
        self.query_one(Markdown).update("## Uploading to Smartsheet...")

    def compose(self) -> ComposeResult:
        yield Markdown("# Parsing CSV...", classes="markdown")


class Browser(ModalScreen):
    def compose(self) -> ComposeResult:
        yield DirectoryTree(INPUTS_DIR)

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        self.dismiss(event.path)


class MainApp(App):
    CSS_PATH = "src/gui.tcss"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]
    csv = reactive(utils.get_latest_csv())
    date = reactive(TODAY)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("CSV to Upload. Defaults to most recent CSV.")
        yield Input(
            id="file",
            value="",
            placeholder="Enter the latest CSV file...",
            validators=[Function(utils.is_valid_file, "Not a valid file.")],
        )
        yield Label(id="file_label")
        with Horizontal():
            yield Button("Get Recent", id="recent", variant="default")
            yield Button("Browse", id="browse", variant="primary")

        yield Rule(line_style="heavy")

        yield Label("Date for the upload.")
        with Horizontal(classes="inputs"):
            yield Input(
                id="date",
                placeholder="Enter date for upload...",
                validators=[Function(utils.is_valid_date, "Not a valid date.")],
            )
        yield Label(id="date_label")
        yield Button("Today", id="today", variant="default")

        yield Rule(line_style="heavy")

        with Horizontal():
            yield Button("Submit", id="submit", variant="success")
            yield Button("Exit", id="exit", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Diamonds Program"
        self.query_one("#file").focus()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    @on(Input.Changed)
    def show_invalid_reasons(self, event: Input.Changed) -> None:
        # Updating the UI to show the reasons why validation failed
        def update_label(control: str, msg: str) -> None:
            self.query_one(f"#{control.id}_label").update(msg)

        if not event.validation_result.is_valid:
            update_label(event.control, event.validation_result.failure_descriptions[0])
        else:
            update_label(event.control, "Valid")

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
            case "submit":
                file = self.query_one("#file")
                date = self.query_one("#date")
                if all((file.value, date.value)) and all((file.is_valid, date.is_valid)):
                    self.csv = file.value
                    self.date = date.value
                    self.main()

    @work
    async def main(self) -> None:
        """
        - row updates are to-bottom. if dates are before existing, it will not be in order
        - will not ignore if duplicate date
        - add more stuff to output
        - split row updates to await them?
        """
        wait_screen = Waiting()
        await self.push_screen(wait_screen)
        df, ss = await asyncio.gather(get_df(self.csv), get_ss())
        wait_screen.post_message(Waiting.Change())
        new_vendors = await update_smartsheet(df, ss, self.date)

        x = "\n- " + "\n- ".join(new_vendors)
        output = f"""\
        New Vendors

        {x}
        """

        self.pop_screen()
        await self.push_screen(Output(output))


async def get_df(csv):
    # import pandas as pd
    #
    # return pd.read_json("df.json")
    return data.create_output_df(INPUTS_DIR + csv)
    # self.df.to_json("df.json")


async def get_ss():
    SHEET_NAME = "COPYYYYYYY of Count of URL Status 2024"
    TOKEN = "FF8W4twmkyxslTkWRqLabgnI0odHKPhUk5V7S"
    ssheet = ss.SSheet(TOKEN)
    ssheet.get_sheet(SHEET_NAME)
    ssheet.get_parents_first_column()
    ss_vendors = list(ssheet.parent_rows.keys())
    return ssheet, ss_vendors


async def update_smartsheet(df, ss, date):
    new_vendors = utils.filter_list(df["Vendor"], ss[1])
    for vendor in new_vendors:
        ss[0].add_new_row_first_col("Vendor", vendor, update_parents=True)

    ss[0].add_child_rows_to_sheet(df, date)
    return new_vendors


app = MainApp()
if __name__ == "__main__":
    app.run()
