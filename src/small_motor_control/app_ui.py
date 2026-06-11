from pathlib import Path

from pydoover import ui

from .app_tags import SmallMotorControlTags


class SmallMotorControlUI(ui.UI, display_name=SmallMotorControlTags.app_display_name):
    ignition_on = ui.BooleanVariable(
        "Ignition On",
        name="ignition_on",
        value=SmallMotorControlTags.ignition_on,
    )
    is_running = ui.BooleanVariable(
        "Engine Running",
        name="is_running",
        value=SmallMotorControlTags.is_running,
    )

    start_now = ui.Button(
        "Start Engine",
        name="start_now",
        colour=ui.Colour.green,
        requires_confirm=True,
        hidden=SmallMotorControlTags.start_now_hidden,
    )
    stop_now = ui.Button(
        "Stop Engine",
        name="stop_now",
        colour=ui.Colour.red,
        requires_confirm=False,
        hidden=SmallMotorControlTags.stop_now_hidden,
    )
    clear_error = ui.Button(
        "Clear Error",
        name="clear_error",
        colour=ui.Colour.blue,
        requires_confirm=False,
        hidden=SmallMotorControlTags.clear_error_hidden,
    )

    auto_reason = ui.TextVariable(
        "Running for",
        name="auto_reason",
        value=SmallMotorControlTags.run_request_reason,
        hidden=SmallMotorControlTags.auto_reason_hidden,
    )

    estop_warning = ui.WarningIndicator(
        "Engine Estopped",
        name="estop_warning",
        hidden=SmallMotorControlTags.estop_warning_hidden,
    )
    error_warning = ui.WarningIndicator(
        "Problem Starting Engine",
        name="error_warning",
        hidden=SmallMotorControlTags.error_warning_hidden,
    )
    manual_mode_warning = ui.WarningIndicator(
        "Engine in Manual Mode - No Remote Control",
        name="manual_mode_warning",
        hidden=SmallMotorControlTags.manual_mode_warning_hidden,
    )


def export():
    SmallMotorControlUI(None, None, None).export(
        Path(__file__).parents[2] / "doover_config.json",
        "small_motor_control",
    )
