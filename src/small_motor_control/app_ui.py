from pydoover import ui


class SmallMotorControlUI:
    def __init__(self):

        self.ignition_on = ui.BooleanVariable("ignition_on", "Ignition On")
        self.is_running = ui.BooleanVariable("is_running", "Motor Running")

        self.start_now = ui.Action("start_now", "Start Motor", colour=ui.Colour.green, requires_confirm=True)
        self.stop_now = ui.Action("stop_now", "Stop Motor", colour=ui.Colour.red, requires_confirm=False, hidden=True)

        self.manual_mode_warning = ui.WarningIndicator("manual_mode_warning", "Manual Mode - No Remote Control", hidden=True)

    def fetch(self):
        return self.ignition_on, self.is_running, self.start_now, self.stop_now, self.manual_mode_warning

    def update(self, ignition_on: bool, is_running: bool, manual_mode: bool):
        self.ignition_on.update(ignition_on)
        self.is_running.update(is_running)
        
        if manual_mode:
            self.manual_mode_warning.hidden = False
            self.start_now.hidden = True
            self.stop_now.hidden = True
        elif is_running:
            self.manual_mode_warning.hidden = True
            self.start_now.hidden = True
            self.stop_now.hidden = False
        else:
            self.manual_mode_warning.hidden = True
            self.start_now.hidden = False
            self.stop_now.hidden = True

