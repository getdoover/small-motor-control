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
        self.state = SmallMotorControlState()

        self.loop_target_period = 0.25  # seconds

        self._last_ignition_input = None
        self._last_no_charge_input = None

        self.start_attempt: StartAttempt | None = None

    async def setup(self):
        self.ui_manager.set_display_name("Motor")
        self.ui_manager.add_children(*self.ui.fetch())
        await self.update_inputs()

    async def main_loop(self):
        log.info(f"State is: {self.state.state}")

        await self.spin_state()

        ## Do different things based on the state
        if self.state.state in [
                "ignition_off",
                "ignition_manual_on",
                "running_manual",
            ]:
            self.start_attempt = None
            await self.set_ignition(False)
            await self.set_starter(False)
            await self.set_horn(False)

        elif self.state.state == "starting_auto":
            if self.start_attempt is None:
                self.start_attempt = StartAttempt(time.time())
        
            await self.set_ignition(self.start_attempt.get_ignition_state())
            await self.set_starter(self.start_attempt.get_starter_state())
            await self.set_horn(self.start_attempt.get_horn_state())

        elif self.state.state == "running_auto":
            await self.set_ignition(True)
            await self.set_starter(False)
            await self.set_horn(False)

        self.ui.update(
            ignition_on=self.last_ignition_input,
            is_running=self.get_io_is_running(),
            manual_mode=self.state.state in ["ignition_manual_on", "running_manual"],
        )

    async def update_inputs(self):
        # This is where you would read inputs from the device

        ## For getting either digital or analog inputs
        async def get_input(pin):
            if pin > 3:
                return await self.platform_iface.get_ai_async(pin - 4)
            else:
                return await self.platform_iface.get_di_async(pin)

        self._last_ignition_input = await get_input(self.config.ignition_in_pin.value)
        self._last_no_charge_input = await get_input(self.config.no_charge_in_pin.value)


    async def spin_state(self): 
        await self.update_inputs()

        last_state = None
        ## keep spinning until state has stabilised
        while last_state != self.state:
            last_state = self.state
            await self.evaluate_state()
            log.info(f"State spin complete for {self.name} - {self.state}")

        ## Clear the UI actions after evaluating the state
        self.ui.start_now.coerce(None)
        self.ui.stop_now.coerce(None)

    async def evaluate_state(self):
        s = self.state.state

        if s == "ignition_off":
            if self.last_ignition_input:
                await self.state.ignition_detected_on()
            if self.check_start_command():
                await self.state.run_start()

        elif s == "ignition_manual_on":
            if not self.last_ignition_input:
                await self.state.ignition_detected_off()
            if self.get_io_is_running():
                await self.state.manual_start()

        elif s == "running_manual":
            if not self.last_ignition_input:
                await self.state.ignition_detected_off()
            elif not self.get_io_is_running():
                await self.state.ignition_detected_off()

        elif s == "starting_auto":
            if self.get_io_is_running():
                await self.state.has_started()
            elif self.check_stop_command():
                await self.state.stop_motor()

        elif s == "running_auto":
            if not self.get_io_is_running():
                await self.state.stop_motor()
            elif self.check_stop_command():
                await self.state.stop_motor()

    def check_start_command(self):
        # This is where you would check for a start command, e.g., from a button press
        return self.ui.start_now.current_value
    
    def check_stop_command(self):
        # This is where you would check for a stop command, e.g., from a button press
        return self.ui.stop_now.current_value

    def get_io_is_running(self) -> bool:
        if self.last_ignition_input and not self.last_no_charge_input:
            return True
        return False
    
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

    @ui.callback("send_alert")
    async def on_send_alert(self, new_value):
        log.info(f"Sending alert: {self.ui.test_output.current_value}")
        await self.publish_to_channel("significantAlerts", self.ui.test_output.current_value)
        self.ui.send_alert.coerce(None)