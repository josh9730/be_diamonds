import logging
import traceback
from io import StringIO
from pathlib import Path
from typing import Callable

import pandas as pd
from nicegui import app, events, run, ui

from src import utils
from src.constants import *
from src.main import Main

LOG_DIR = Path("logs/")
if not LOG_DIR.exists():
    LOG_DIR.mkdir()


#
# Launcher functions
#


async def run_func(func: Callable, date: str, ss_name: str, waiting: ui.dialog, final: ui.dialog) -> None:
    """Main function for running the user-selected action."""
    main.date = date
    main.ss_name = ss_name

    waiting.visible = True
    await run.cpu_bound(func)
    waiting.visible = False
    final.visible = True


def next_action(action: str) -> None:
    """Navigate to the next page."""
    if main.input_df is not None:
        ui.navigate.to(f"/{action}")


#
# Helpers
#


def add_seps():
    ui.space()
    ui.separator()
    ui.space()


def header(title: str):
    with ui.header(elevated=True).style("background-color: #3874c8").classes("items-center justify-between"):
        ui.label(title).classes("text-lg font-bold")


def sheet_name(sheet_name: str, label: str = "Smartsheet Name"):
    return ui.input(label=label, value=sheet_name).classes("w-80")


def sheet_date_ui():
    with ui.input("Date", value=utils.TODAY) as date:
        with date.add_slot("append"):
            ui.icon("edit_calendar").on("click", lambda: menu.open()).classes("cursor-pointer")
        with ui.menu() as menu:
            ui.date().bind_value(date)
    return date


def waiting_diag() -> ui.dialog:
    with ui.dialog() as waiting, ui.card():
        waiting.props("persistent")
        waiting.visible = False
        ui.label("Working, this may take several minutes...")
    waiting.open()
    return waiting


def final_diag() -> ui.dialog:
    with ui.dialog() as final, ui.card():
        final.props("persistent")
        final.visible = False
        ui.label("Finished!")
        ui.button("Close", on_click=lambda: reset_ui(final))
    final.open()
    return final


def reset_ui(diag: ui.dialog):
    diag.visible = False
    ui.navigate.to("/")
    csv.reset()


#
#  Vendor Audit Page
#


def vendors_checkbox():
    """Helper func for vendor check

    - checkboxes are bound to the True/False values of selected_vendors
    """
    main.csv_vendors()
    with ui.grid(columns=3):
        for vendor in main.selected_vendors:
            ui.checkbox(vendor).bind_value(main.selected_vendors, vendor).classes("h-2")


@ui.page("/vendors")
def vendors_page():
    """Page for launching vendor audits.

    - audit_all switch is bound to selected_vendors. Toggling the switch sets all vendors to True or False.
    """
    with ui.row():
        ss_name = sheet_name(utils.get_sheet_name("audit"))
        date = sheet_date_ui()
    header("Vendor Audits")
    radio = ui.radio(["Weekly Audit", "Deep Dive"], value="Weekly Audit").props("inline")
    audit_all = ui.switch("Audit All Vendors?", value=False).bind_value_to(
        main.selected_vendors, forward=lambda e: main.selected_vendors.update((i, e) for i in main.selected_vendors)
    )
    add_seps()
    ui.label("Vendor Selection").classes("font-bold").style("color: red")
    vendors_checkbox()
    add_seps()

    ui.button("Run", on_click=lambda: run_func(main.run_audits, date.value, ss_name.value, waiting, final))


#
#  Coverages Page
#


@ui.page("/coverages")
def coverages_page():
    header("Coverages Upload")
    with ui.row():
        ss_name = sheet_name(utils.get_sheet_name("coverages"))
        date = sheet_date_ui()
    waiting = waiting_diag()
    final = final_diag()
    ui.button("Run", on_click=lambda: run_func(main.run_coverages, date.value, ss_name.value, waiting, final))


#
# Both functions page
#


@ui.page("/both")
def both_page():
    header("Coverages and Vendor Audits")
    date = sheet_date_ui()
    with ui.row():
        coverages_name = sheet_name(utils.get_sheet_name("coverages"), "Coverages Sheet")
        audits_name = sheet_name(utils.get_sheet_name("audit"), "Vendor Audits Sheet")
    waiting = waiting_diag()
    final = final_diag()
    ui.button("Run", on_click=lambda: run_func(main.run_both, date.value, ss_name.value, waiting, final))


#
# Main Page
#

main = Main()
header(UI_TITLE)
ui.label("Upload the new CSV.").classes("font-bold")
csv = (
    ui.upload(
        label="Input CSV",
        auto_upload=True,
        on_rejected=lambda: ui.notify("Incorrect file type."),
        on_upload=lambda e: handle_upload(main, e),
    )
    .props("accept=.csv")
    .classes("max-w-full")
)
add_seps()
ui.label("Select Action:").classes("font-bold")
with ui.row():
    ui.button("Coverages", color="green", on_click=lambda: next_action("coverages"))
    ui.button("Vendor Audit", color="grey", on_click=lambda: next_action("vendors"))
    ui.button("Coverages & Audit", on_click=lambda: next_action("both"))

with ui.dialog() as waiting, ui.card():
    waiting.props("persistent")
    waiting.visible = False
    ui.label("Working, this may take several minutes...")
waiting.open()
with ui.dialog() as final, ui.card():
    final.props("persistent")
    final.visible = False
    ui.label("Finished!")
    ui.button("Close", on_click=lambda: reset_ui(final))
final.open()


#
# Handlers, Exceptions
#


def handle_upload(main, e: events.UploadEventArguments):
    with StringIO(e.content.read().decode()) as f:
        main.input_df = pd.read_csv(f)


def handle_exception(err):
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=f"{LOG_DIR}/{utils.TODAY}.log", encoding="utf-8", level=logging.DEBUG, filemode="w")
    logger.error(err, exc_info=True, stack_info=True)

    with ui.dialog() as err_dialog, ui.card():
        err_dialog.props("persistent")
        ui.label("An error has occured and been logged!")
        ui.button("Close", on_click=lambda: reset_ui(err_dialog))
    err_dialog.open()


#
# Start UI
#

ui.run(dark=True)
app.on_exception(lambda err: handle_exception(traceback.format_exception(err)))
