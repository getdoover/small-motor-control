from pydoover import ui


class SmallMotorControlUI:
    def __init__(self):

        self.is_running = ui.BooleanVariable("is_running", "Motor Running")

        self.start_now = ui.Action("start_now", "Start Motor", colour=ui.Colour.green, requires_confirm=True)
        self.stop_now = ui.Action("stop_now", "Stop Motor", colour=ui.Colour.red, requires_confirm=False, hidden=True)


    def fetch(self):
        return self.is_running, self.start_now, self.stop_now

    def update(self, is_running: bool):
        self.is_running.update(is_running)
        
        if is_running:
            self.start_now.hidden = True
            self.stop_now.hidden = False
        else:
            self.start_now.hidden = False
            self.stop_now.hidden = True
            
