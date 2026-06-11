import logging
import time

from pydoover.docker import Application

from .app_config import SmallMotorControlConfig
from .app_state import SmallMotorControlState
from .app_tags import SmallMotorControlTags
from .app_ui import SmallMotorControlUI

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
    config_cls = SmallMotorControlConfig
    tags_cls = SmallMotorControlTags
    ui_cls = SmallMotorControlUI

    async def setup(self):
        self.started = time.time()
        self.state = SmallMotorControlState(self)

        self.loop_target_period = 0.5  # seconds

        self.last_error = None

        self._last_estop_input = None
        self._last_ignition_input = None
        self._last_no_charge_input = None

        self._last_ignition_output = None
        self._last_starter_output = None
        self._last_horn_output = None

        self._last_io_is_running = None
        self._last_io_is_running_change = time.time()

        self.start_attempt: StartAttempt | None = None

        # pending UI commands, set by the button handlers and consumed
        # (then cleared) by the state machine each loop.
        self._start_command = False
        self._stop_command = False
        self._clear_error_command = False

        await self.update_inputs()

    async def main_loop(self):

        await self.update_inputs()

        state = await self.state.spin_state()
        ## Clear the UI commands after evaluating the state
        self._start_command = False
        self._stop_command = False
        self._clear_error_command = False

        await self.update_tags(state)

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

    @ui.handler("start_now")
    async def on_start_now(self, ctx: ui.InteractionContext, _value):
        self._start_command = True

    @ui.handler("stop_now")
    async def on_stop_now(self, ctx: ui.InteractionContext, _value):
        self._stop_command = True

    @ui.handler("clear_error")
    async def on_clear_error(self, ctx: ui.InteractionContext, _value):
        self._clear_error_command = True

    async def update_inputs(self):
        # This is where you would read inputs from the device

        ## For getting either digital or analog inputs
        async def get_input(pin):
            if pin > 3:
                return await self.platform_iface.fetch_ai(pin - 4)
            else:
                return await self.platform_iface.fetch_di(pin)

        self._last_estop_input = await get_input(self.config.estop_in_pin.value)
        self._last_ignition_input = await get_input(self.config.ignition_in_pin.value)
        self._last_no_charge_input = await get_input(self.config.no_charge_in_pin.value)

    async def update_tags(self, state: str):
        await self.tags.state.set(self.state.state)
        await self.tags.app_display_name.set(f"{self.app_display_name} - {self.state.get_state_string()}")

        await self.tags.ignition_on.set(self.last_ignition_input)
        await self.tags.is_running.set(self.get_io_is_running())

        ## Show exactly one control surface, in priority order
        estopped = state == "estopped"
        errored = not estopped and self.last_error is not None
        manual = not estopped and not errored and state in ["ignition_manual_on", "running_manual"]
        auto = (
                not estopped and not errored and not manual
                and self.run_request_reason() is not None
        )
        stoppable = (
                not estopped and not errored and not manual and not auto
                and (self.get_io_is_running() or "starting" in state)
        )
        startable = not (estopped or errored or manual or auto or stoppable)

        await self.tags.estop_warning_hidden.set(not estopped)
        await self.tags.error_warning_hidden.set(not errored)
        await self.tags.clear_error_hidden.set(not errored)
        await self.tags.manual_mode_warning_hidden.set(not manual)
        await self.tags.auto_reason_hidden.set(not auto)
        await self.tags.stop_now_hidden.set(not stoppable)
        await self.tags.start_now_hidden.set(not startable)

    def has_run_request(self) -> bool:
        return self.run_request_reason() is not None

    def run_request_reason(self) -> str | None:
        return self.tags.run_request_reason.get()

    def check_start_command(self):
        # Set by the start_now button handler
        return self._start_command

    def check_stop_command(self):
        # Set by the stop_now button handler
        return self._stop_command

    def check_clear_error_command(self):
        # Set by the clear_error button handler
        return self._clear_error_command

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
        if state != self._last_ignition_output:
            if self.config.ignition_out_pin.value > 5:
                await self.platform_iface.set_ao(self.config.ignition_out_pin.value - 6, 100 if state else 0)
            else:
                await self.platform_iface.set_do(self.config.ignition_out_pin.value, state)
        self._last_ignition_output = state

    async def set_starter(self, state: bool):
        log.debug(f"Setting starter to {state} on pin {self.config.starter_pin.value}")
        if state != self._last_starter_output:
            if self.config.starter_pin.value > 5:
                await self.platform_iface.set_ao(self.config.starter_pin.value - 6, 100 if state else 0)
            else:
                await self.platform_iface.set_do(self.config.starter_pin.value, state)
        self._last_starter_output = state

    async def set_horn(self, state: bool):
        log.debug(f"Setting horn to {state} on pin {self.config.horn_pin.value}")
        if state != self._last_horn_output:
            if self.config.horn_pin.value > 5:
                await self.platform_iface.set_ao(self.config.horn_pin.value - 6, 100 if state else 0)
            else:
                await self.platform_iface.set_do(self.config.horn_pin.value, state)
        self._last_horn_output = state
