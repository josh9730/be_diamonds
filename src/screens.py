from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, DirectoryTree, Markdown, Pretty, Rule

from src import utils


class Output(Screen):
    def __init__(self, output: str) -> None:
        self.output = output
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Markdown(f"# Completed uploads for {utils.TODAY}")
        yield Button("Finish", classes="final", variant="primary")
        yield Rule(line_style="heavy")
        yield Markdown("## New Vendors: ")
        yield Pretty(self.output)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.exit()


class Waiting(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Markdown("# Working...\n This may take several minutes.", classes="waiting")


class Browser(ModalScreen):
    def compose(self) -> ComposeResult:
        yield DirectoryTree(utils.INPUTS_DIR)

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.dismiss(event.path)


class ErrApp(App):
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
    ]
    ENABLE_COMMAND_PALETTE = False

    def compose(self) -> ComposeResult:
        yield Markdown("# Something went wrong!")
        yield Button("Exit", id="exit", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.exit()
