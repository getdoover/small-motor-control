from pathlib import Path

from pydoover import config


class SmallMotorControlConfig(config.Schema):
    def __init__(self):
        # these 2 are device specific, and inherit from the device-set variables.
        # However, the user can override them if they wish.

        self.ignition_in_pin = config.Integer(
            "Ignition In Pin",
            description="This pin is used to detect the ignition state. AI are Pin 4-5",
            default=1,
            minimum=0,
        )
        self.no_charge_in_pin = config.Integer(
            "No Charge In Pin",
            description="This pin is used to detect the alternator charging state. AI are Pin 4-5",
            default=2,
            minimum=0,
        )
        self.ignition_out_pin = config.Integer(
            "Ignition Out Pin",
            description="This pin is used to control the ignition relay. AO are Pin 6-7",
            default=0,
            minimum=0,
        )
        self.starter_pin = config.Integer(
            "Starter Pin",
            description="This pin is used to control the starter relay. AO are Pin 6-7",
            default=6,
            minimum=0,
        )
        self.horn_pin = config.Integer(
            "Horn Pin",
            description="This pin is used to control the horn relay. AO are Pin 6-7",
            default=7,
            minimum=0,
        )
        
        # self.sim_app_key = config.Application("Simulator App Key", description="The app key for the simulator")


if __name__ == "__main__":
    SmallMotorControlConfig().export(Path(__file__).parent.parent.parent / "doover_config.json", "small_motor_control")
