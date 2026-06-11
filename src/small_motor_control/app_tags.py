from pydoover import tags


class SmallMotorControlTags(tags.Tags):
    # Bound to the app's display string in the UI ("<name> - <state>").
    app_display_name = tags.String(default="Engine")
    state = tags.String(default="ignition_off")

    ignition_on = tags.Boolean(default=False, live=True)
    is_running = tags.Boolean(default=False, live=True)

    # Set by other apps to request the motor to run; cleared to let it stop.
    run_request_reason = tags.String(default=None)

    # Visibility flags for the state-driven UI elements. Exactly one control
    # surface is shown at a time, driven from the state machine each loop.
    start_now_hidden = tags.Boolean(default=False)
    stop_now_hidden = tags.Boolean(default=True)
    clear_error_hidden = tags.Boolean(default=True)
    auto_reason_hidden = tags.Boolean(default=True)
    estop_warning_hidden = tags.Boolean(default=True)
    error_warning_hidden = tags.Boolean(default=True)
    manual_mode_warning_hidden = tags.Boolean(default=True)
