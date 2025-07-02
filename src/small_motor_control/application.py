import logging
import time

from pydoover.docker import Application
from pydoover import ui

from .app_config import SmallMotorControlConfig
from .app_ui import SmallMotorControlUI
from .app_state import SmallMotorControlState

# Set up logging
log = logging.getLogger()


class StartAttempt:

    def __init__(self, start_time: float):
        self.start_time = start_time

    def get_age(self) -> float:
        return time.time() - self.start_time

    def get_horn_state(self) -> bool:
        # Horn should be on for 3 seconds before start attempt
        if time.time() < self.start_time + 3:
            return True
        if time.time() < self.start_time + 6:
            return False
        if time.time() < self.start_time + 9:
            return True
        return False
    
    def get_ignition_state(self) -> bool:
        # Ignition should be on for 6 seconds before start attempt
        if time.time() < self.start_time + 8:
            return False
        return True
    
    def get_starter_state(self) -> bool:
        # Starter should be on for 6 seconds during start attempts
        if time.time() < self.start_time + 10:
            return False
        if time.time() < self.start_time + 16:
            return True
        if time.time() < self.start_time + 22:
            return False
        if time.time() < self.start_time + 28:
            return True
        return False
    

class SmallMotorControlApplication(Application):
    config: SmallMotorControlConfig  # not necessary, but helps your IDE provide autocomplete!

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.started = time.time()
        self.ui = SmallMotorControlUI()
        self.state = SmallMotorControlState(self)

        self.loop_target_period = 0.5  # seconds

        self.last_error = None

        self._last_estop_input = None
        self._last_ignition_input = None
        self._last_no_charge_input = None

        self._last_io_is_running = None
        self._last_io_is_running_change = time.time()

        self._last_run_request_reason = None
        self._last_run_request_change = time.time()

        self.start_attempt: StartAttempt | None = None

    async def setup(self):
        self.ui_manager.set_display_name(self.config.display_name.value)
        self.ui_manager.add_children(*self.ui.fetch())
        await self.update_inputs()

    async def main_loop(self):

        await self.update_inputs()

        state = await self.state.spin_state()
        ## Clear the UI actions after evaluating the state
        self.ui.start_now.coerce(None)
        self.ui.stop_now.coerce(None)
        self.ui.clear_error.coerce(None)

        await self.update_tags()

        ## Do different things based on the state
        if state in [
                "ignition_off",
                "ignition_manual_on",
                "running_manual",
                "estopped",
                "error",
            ]:
            self.start_attempt = None
            await self.set_ignition(False)
            await self.set_starter(False)
            await self.set_horn(False)

        elif state in ["starting_user", "starting_auto"]:
            ## If we are starting, we need to set the ignition and starter based on the start attempt
            if self.start_attempt is None:
                self.start_attempt = StartAttempt(time.time())
        
            await self.set_ignition(self.start_attempt.get_ignition_state())
            await self.set_starter(self.start_attempt.get_starter_state())
            await self.set_horn(self.start_attempt.get_horn_state())

        elif state in ["running_user", "running_auto"]:
            self.start_attempt = None
            await self.set_ignition(True)
            await self.set_starter(False)
            await self.set_horn(False)

        ## Update the display string
        self.ui_manager.set_display_name(self.config.display_name.value + " - " + self.state.get_state_string())
        self.ui.update(
            estopped=state == "estopped",
            ignition_on=(self.last_ignition_input),
            is_running=(self.get_io_is_running()),
            manual_mode=state in ["ignition_manual_on", "running_manual"],
            auto_running_reason=self.run_request_reason(),
            error=self.last_error,
        )

    async def update_inputs(self):
        # This is where you would read inputs from the device

        ## For getting either digital or analog inputs
        async def get_input(pin):
            if pin > 3:
                return await self.platform_iface.get_ai_async(pin - 4)
            else:
                return await self.platform_iface.get_di_async(pin)

        self._last_estop_input = await get_input(self.config.estop_in_pin.value)
        self._last_ignition_input = await get_input(self.config.ignition_in_pin.value)
        self._last_no_charge_input = await get_input(self.config.no_charge_in_pin.value)

    async def update_tags(self):
        await self.set_tag("state", self.state.state)

    def has_run_request(self):
        return self.run_request_reason() is not None

    def run_request_reason(self, grace_period=6) -> str | None:
        run_request = self.get_tag("run_request_reason")
        if run_request != self._last_run_request_reason:
            self._last_run_request_change = time.time()

        if run_request is None and self._last_run_request_reason is not None and \
                time.time() - self._last_run_request_change < grace_period:
            # If the run request has recently nulled, we still consider it valid for a short grace period
            return self._last_run_request_reason
        
        self._last_run_request_reason = run_request
        return run_request

    def check_start_command(self):
        # This is where you would check for a start command, e.g., from a button press
        return self.ui.start_now.current_value
    
    def check_stop_command(self):
        # This is where you would check for a stop command, e.g., from a button press
        return self.ui.stop_now.current_value
    
    def check_clear_error_command(self):
        # This is where you would check for a clear error command, e.g., from a button press
        return self.ui.clear_error.current_value

    def get_io_is_running(self, start_grace_period=2) -> bool:
        if self.last_ignition_input and not self.last_no_charge_input:
            result = True
        else:
            result = False

        if self._last_io_is_running != result:
            self._last_io_is_running_change = time.time()
        self._last_io_is_running = result

        if result and self.get_io_is_running_age() < start_grace_period:
            return False
        return result
        
    def get_io_is_running_age(self) -> float:
        if self._last_io_is_running_change is None:
            return 0
        return time.time() - self._last_io_is_running_change
    
    @property
    def last_estop_input(self):
        if self._last_estop_input is None:
            return False
        if isinstance(self._last_estop_input, bool):
            return self._last_estop_input
        return self._last_estop_input > 2

    @property
    def last_ignition_input(self):
        if self._last_ignition_input is None:
            return False
        if isinstance(self._last_ignition_input, bool):
            return self._last_ignition_input
        return self._last_ignition_input > 2
    
    @property
    def last_no_charge_input(self):
        if self._last_no_charge_input is None:
            return False
        if isinstance(self._last_no_charge_input, bool):
            return self._last_no_charge_input
        return self._last_no_charge_input > 2

    async def set_ignition(self, state: bool):
        log.debug(f"Setting ignition to {state} on pin {self.config.ignition_out_pin.value}")
        if self.config.ignition_out_pin.value > 5:
            await self.platform_iface.set_ao_async(self.config.ignition_out_pin.value - 6, 100 if state else 0)
        else:
            await self.platform_iface.set_do_async(self.config.ignition_out_pin.value, state)

    async def set_starter(self, state: bool):
        log.debug(f"Setting starter to {state} on pin {self.config.starter_pin.value}")
        if self.config.starter_pin.value > 5:
            await self.platform_iface.set_ao_async(self.config.starter_pin.value - 6, 100 if state else 0)
        else:
            await self.platform_iface.set_do_async(self.config.starter_pin.value, state)

    async def set_horn(self, state: bool):
        log.debug(f"Setting horn to {state} on pin {self.config.horn_pin.value}")
        if self.config.horn_pin.value > 5:
            await self.platform_iface.set_ao_async(self.config.horn_pin.value - 6, 100 if state else 0)
        else:
            await self.platform_iface.set_do_async(self.config.horn_pin.value, state)