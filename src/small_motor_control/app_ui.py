from pydoover import ui


class SmallMotorControlUI:
    def __init__(self):

        self.ignition_on = ui.BooleanVariable("ignition_on", "Ignition On")
        self.is_running = ui.BooleanVariable("is_running", "Engine Running")

        self.start_now = ui.Action("start_now", "Start Engine", colour=ui.Colour.green, requires_confirm=True)
        self.stop_now = ui.Action("stop_now", "Stop Engine", colour=ui.Colour.red, requires_confirm=False, hidden=True)
        self.clear_error = ui.Action("clear_error", "Clear Error", colour=ui.Colour.blue, requires_confirm=False, hidden=True)

        self.auto_reason = ui.TextVariable("auto_reason", "Running for", hidden=True)

        self.estop_warning = ui.WarningIndicator("estop_warning", "Engine Estopped", hidden=True)
        self.error_warning = ui.WarningIndicator("error_warning", "Problem Starting Engine", hidden=True)
        self.manual_mode_warning = ui.WarningIndicator("manual_mode_warning", "Engine in Manual Mode - No Remote Control", hidden=True)

    def fetch(self):
        return self.ignition_on, self.is_running, self.start_now, self.stop_now, self.auto_reason, self.estop_warning, self.manual_mode_warning

    def update(self, estopped:bool,  ignition_on: bool, is_running: bool, is_starting: bool, manual_mode: bool, run_request_reason: str | None = None, error: str | None = None):
        self.ignition_on.update(ignition_on)
        self.is_running.update(is_running)
        
        ## hide everything
        self.start_now.hidden = True
        self.stop_now.hidden = True
        self.estop_warning.hidden = True
        self.manual_mode_warning.hidden = True
        self.clear_error.hidden = True

        self.auto_reason.update("")
        self.auto_reason.hidden = True

        ## Now show the appropriate UI elements based on the state
        if estopped:
            self.estop_warning.hidden = False
        elif error is not None:
            self.error_warning.update(hidden=False)
            self.clear_error.hidden = False
        elif manual_mode:
            self.manual_mode_warning.hidden = False
        elif run_request_reason is not None:
            self.auto_reason.hidden = False
            self.auto_reason.update(run_request_reason)
        elif is_running or is_starting:
            self.stop_now.hidden = False
        else:
            self.start_now.hidden = False
