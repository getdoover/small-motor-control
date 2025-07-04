import logging

from pydoover.state import StateMachine

log = logging.getLogger(__name__)

class SmallMotorControlState:
    state: str

    error_timeout = 60 * 60 * 24 * 2  # 2 days

    states = [
        {"name": "ignition_off"},
        {"name": "error", "timeout": error_timeout, "on_timeout": "clear_error"},
        {"name": "estopped"},
        {"name": "ignition_manual_on"},
        {"name": "running_manual"},
        ## These states are used when the user has pressed the start button
        {"name": "starting_user", "timeout": 40, "on_timeout": "stop_motor"},
        {"name": "running_user"},
        ## These states are used when another system has requested the motor to run
        {"name": "starting_auto", "timeout": 40, "on_timeout": "set_error"},
        {"name": "running_auto"},
    ]

    transitions = [
        {"trigger": "ignition_detected_on", "source": "ignition_off", "dest": "ignition_manual_on"},
        {"trigger": "ignition_detected_off", "source": ["ignition_manual_on", "running_manual"], "dest": "ignition_off"},
        {"trigger": "manual_start", "source": "ignition_manual_on", "dest": "running_manual"},
        {"trigger": "user_run_start", "source": "ignition_off", "dest": "starting_user"},
        {"trigger": "user_has_started", "source": "starting_user", "dest": "running_user"},
        {"trigger": "auto_run_start", "source": "ignition_off", "dest": "starting_auto"},
        {"trigger": "auto_has_started", "source": "starting_auto", "dest": "running_auto"},
        {"trigger": "stop_motor", "source": ["starting_user", "running_user", "starting_auto", "running_auto"], "dest": "ignition_off"},
        {"trigger": "estop", "source": "*", "dest": "estopped"},
        {"trigger": "reset_estop", "source": "estopped", "dest": "ignition_off"},
        {"trigger": "error", "source": "*", "dest": "error"},
        {"trigger": "reset_error", "source": "error", "dest": "ignition_off"},
    ]

    def __init__(self, app):
        self.app = app

        self.state_machine = StateMachine(
            states=self.states,
            transitions=self.transitions,
            model=self,
            initial="ignition_off",
            queued=True,
        )

    def get_state_string(self):
        """
        Returns the display string of the current state.
        """
        ## Return a map
        state_strings = {
            "ignition_off": "Off",
            "error": "Error",
            "estopped": "E-Stopped",
            "ignition_manual_on": "Key On",
            "running_manual": "Running",
            "starting_user": "Starting",
            "running_user": "Running",
            "starting_auto": "Starting",
            "running_auto": "Running",
        }

        return state_strings.get(self.state, "Unknown")

    async def spin_state(self): 
        last_state = None
        ## keep spinning until state has stabilised
        while last_state != self.state:
            last_state = self.state
            await self.evaluate_state()
            # log.info(f"State spin complete for {self.name} - {self.state}")

        log.info(f"State is: {self.state}")
        return self.state

    async def evaluate_state(self):
        s = self.state

        ## No matter what state, if the emergency stop is pressed, we go to estopped
        if self.app.last_estop_input:
            await self.estop()

        elif s == "estopped":
            if not self.app.last_estop_input:
                await self.reset_estop()

        elif s == "ignition_off":
            if self.app.last_ignition_input:
                await self.ignition_detected_on()
            if self.app.check_start_command():
                await self.user_run_start()
            if self.app.has_run_request():
                await self.auto_run_start()

        elif s == "ignition_manual_on":
            if not self.app.last_ignition_input:
                await self.ignition_detected_off()
            if self.app.get_io_is_running():
                await self.manual_start()

        elif s == "running_manual":
            if not self.app.last_ignition_input:
                await self.ignition_detected_off()
            elif not self.app.get_io_is_running():
                await self.ignition_detected_off()

        elif s == "starting_user":
            if self.app.get_io_is_running():
                await self.user_has_started()
            elif self.app.check_stop_command():
                await self.stop_motor()

        elif s == "running_user":
            if not self.app.get_io_is_running():
                await self.stop_motor()
            elif self.app.check_stop_command():
                await self.stop_motor()

        elif s == "starting_auto":
            if self.app.get_io_is_running():
                await self.auto_has_started()
            elif not self.app.has_run_request():
                await self.stop_motor()

        elif s == "running_auto":
            if not self.app.get_io_is_running():
                await self.stop_motor()
            elif not self.app.has_run_request():
                await self.stop_motor()

    def set_error(self, error: str = "Error occurred"):
        """
        Set the state to error.
        """
        log.error("Setting state to error")
        self.error()
        self.app.last_error = error

    def reset_error(self):
        """
        Reset the error state.
        """
        log.info("Resetting error state")
        self.reset_error()
        self.app.last_error = None