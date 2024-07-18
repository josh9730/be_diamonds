import multiprocessing  # noqa

multiprocessing.freeze_support()  # noqa

import logging
import traceback
from io import StringIO
from pathlib import Path
from typing import Callable

import pandas as pd
from nicegui import app, events, run, ui, native

from src import utils
from src.constants import *
from src.help_md import main_help
from src.main import Main

LOG_DIR = Path("logs/")
if not LOG_DIR.exists():
    LOG_DIR.mkdir()

AUDIT_SHEET_NAME: Final[str] = "Colorless Diamond Audit"
COVERAGES_SHEET_NAME: Final[str] = "Diamond Video Coverage Tracker 2024"


#
# Launcher functions
#


async def run_func(
    func: Callable,
    waiting: ui.dialog,
    final: ui.dialog,
    date: str,
    coverages_name: str = None,
    audit_name: str = None,
    audit_num: int = 0,
) -> None:
    """Main function for running the user-selected action."""
    main.date = date
    main.coverages_sheet_name = coverages_name
    main.audit_sheet_name = audit_name
    main.audit_num = int(audit_num)

    waiting.visible = True
    await run.cpu_bound(func)
    waiting.visible = False
    final.visible = True


def next_action(action: str) -> None:
    """Navigate to the next page. CSV must be uploaded"""
    if main.input_df is not None:
        ui.navigate.to(f"/{action}")


#
# Handlers
#


def handle_upload(main, e: events.UploadEventArguments):
    """Parse input file as DataFrame."""
    with StringIO(e.content.read().decode()) as f:
        main.input_df = pd.read_csv(f)


def handle_exception(err):
    """Log event, open error dialog, and reset to main page once clicked."""
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=f"{LOG_DIR}/{utils.TODAY}.log", encoding="utf-8", level=logging.DEBUG, filemode="w")
    logger.error(err, exc_info=True, stack_info=True)

    with ui.dialog() as err_dialog, ui.card():
        err_dialog.props("persistent")
        ui.label("An error has occured and been logged!")
        ui.button("Close", on_click=reset_ui)
    err_dialog.open()


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
        ui.button("Close", on_click=reset_ui)
    final.open()
    return final


def reset_ui():
    """Resets UI to main page."""
    main.input_df = None
    ui.navigate.to("/")
    main.input_df = None


#
#  Vendor Audit Page
#


def vendors_checkbox():
    """Helper func for vendor check.

    - checkboxes are bound to the True/False values of selected_vendors
    """
    main.csv_vendors()
    with ui.scroll_area():
        with ui.grid(columns=3):
            for vendor in main.selected_vendors:
                ui.checkbox(vendor).bind_value(main.selected_vendors, vendor).classes("h-2")


@ui.page("/vendors")
def vendors_page():
    """Page for launching vendor audits.

    - audit_all switch is bound to selected_vendors. Toggling the switch sets all vendors to True or False.
    """
    waiting = waiting_diag()
    final = final_diag()
    header("Vendor Audits")
    with ui.row():
        ss_name = sheet_name(AUDIT_SHEET_NAME)
        date = sheet_date_ui()
    with ui.row():
        radio = ui.radio({10: "Weekly Audit", 1000: "Deep Dive"}, value=10).props("inline")
        audit_num = ui.number(label="Custom Audit Count").bind_value_from(radio)
    ui.switch("Audit All Vendors?", value=False).bind_value_to(
        main.selected_vendors, forward=lambda e: main.selected_vendors.update((i, e) for i in main.selected_vendors)
    )
    add_seps()
    ui.label("Vendor Selection").classes("font-bold").style("color: red")
    vendors_checkbox()
    add_seps()

    #
    # Need to prevent running without selecting at least one vendor
    #
    ui.button(
        "Run",
        color="green",
        on_click=lambda: run_func(
            main.run_audits, waiting, final, date.value, audit_name=ss_name.value, audit_num=audit_num.value
        ),
    )


#
#  Coverages Page
#


@ui.page("/coverages")
def coverages_page():
    """Page for launching Coverages uploads."""
    waiting = waiting_diag()
    final = final_diag()
    header("Coverages Upload")
    with ui.row():
        ss_name = sheet_name(COVERAGES_SHEET_NAME)
        date = sheet_date_ui()

    ui.button(
        "Run",
        color="green",
        on_click=lambda: run_func(main.run_coverages, waiting, final, date.value, coverages_name=ss_name.value),
    )


#
# Both functions page
#


@ui.page("/both")
def both_page():
    waiting = waiting_diag()
    final = final_diag()
    header("Coverages Upload and Vendor Audits")
    with ui.row():
        coverages_name = sheet_name(COVERAGES_SHEET_NAME, "Coverages Sheet")
        audits_name = sheet_name(AUDIT_SHEET_NAME, "Vendor Audits Sheet")
    date = sheet_date_ui()
    with ui.row():
        radio = ui.radio({10: "Weekly Audit", 1000: "Deep Dive"}, value=10).props("inline")
        audit_num = ui.number(label="Custom Audit Count").bind_value_from(radio)
    ui.switch("Audit All Vendors?", value=False).bind_value_to(
        main.selected_vendors, forward=lambda e: main.selected_vendors.update((i, e) for i in main.selected_vendors)
    )
    add_seps()
    ui.label("Vendor Selection").classes("font-bold").style("color: red")
    vendors_checkbox()
    add_seps()

    ui.button(
        "Run",
        color="green",
        on_click=lambda: run_func(
            main.run_both,
            waiting,
            final,
            date.value,
            coverages_name=coverages_name.value,
            audit_name=audits_name.value,
            audit_num=audit_num.value,
        ),
    )


#
# Main Page
#


@ui.page("/")
def main_page():
    header(UI_TITLE)
    with ui.tabs().classes("w-full") as tabs:
        program_tab = ui.tab("Program", icon="home")
        help_tab = ui.tab("Help", icon="info")

    with ui.tab_panels(tabs, value=program_tab).classes("w-full"):
        with ui.tab_panel(program_tab):
            ui.label("See 'Help' for more information!")
            add_seps()
            ui.label("Upload the new CSV.").classes("font-bold")
            ui.upload(
                label="Input CSV",
                auto_upload=True,
                on_rejected=lambda: ui.notify("Incorrect file type."),
                on_upload=lambda e: handle_upload(main, e),
            ).props("accept=.csv").classes("max-w-full")
            add_seps()
            ui.label("Select Action:").classes("font-bold")
            with ui.row():
                ui.button("Coverages", color="green", on_click=lambda: next_action("coverages"))
                ui.button("Vendor Audit", color="grey", on_click=lambda: next_action("vendors"))
                ui.button("Coverages & Audit", on_click=lambda: next_action("both"))

        with ui.tab_panel(help_tab):
            ui.markdown(main_help)


#
# Start UI
#

main = Main()
app.on_exception(lambda err: handle_exception(traceback.format_exception(err)))
ui.run(dark=True, reload=False, native=True, port=native.find_open_port())
