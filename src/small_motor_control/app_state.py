import logging

from pydoover.state import StateMachine

log = logging.getLogger(__name__)

class SmallMotorControlState:
    state: str

    states = [
        {"name": "ignition_off"},
        {"name": "ignition_manual_on"},
        {"name": "running_manual"},
        {"name": "starting_auto", "timeout": 40, "on_timeout": "stop_motor"},
        {"name": "running_auto"},
    ]

    transitions = [
        {"trigger": "ignition_detected_on", "source": "ignition_off", "dest": "ignition_manual_on"},
        {"trigger": "ignition_detected_off", "source": ["ignition_manual_on", "running_manual"], "dest": "ignition_off"},
        {"trigger": "run_start", "source": "ignition_off", "dest": "starting_auto"},
        {"trigger": "has_started", "source": "starting_auto", "dest": "running_auto"},
        {"trigger": "stop_motor", "source": ["starting_auto", "running_auto"], "dest": "ignition_off"},
    ]

    def __init__(self):
        self.state_machine = StateMachine(
            states=self.states,
            transitions=self.transitions,
            model=self,
            initial="ignition_off",
            queued=True,
        )