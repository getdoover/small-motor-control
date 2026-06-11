from pathlib import Path

from pydoover import config


class SmallMotorControlConfig(config.Schema):
    ignition_in_pin = config.Integer(
        "Ignition In Pin",
        description="This pin is used to detect the ignition state. AI are Pin 4-5",
        default=4,
        minimum=0,
    )
    no_charge_in_pin = config.Integer(
        "No Charge In Pin",
        description="This pin is used to detect the alternator charging state. AI are Pin 4-5",
        default=5,
        minimum=0,
    )
    estop_in_pin = config.Integer(
        "Estop In Pin",
        description="This pin is used to detect the emergency stop state. AI are Pin 4-5",
        default=0,
        minimum=0,
    )
    ignition_out_pin = config.Integer(
        "Ignition Out Pin",
        description="This pin is used to control the ignition relay. AO are Pin 6-7",
        default=0,
        minimum=0,
    )
    starter_pin = config.Integer(
        "Starter Pin",
        description="This pin is used to control the starter relay. AO are Pin 6-7",
        default=6,
        minimum=0,
    )
    horn_pin = config.Integer(
        "Horn Pin",
        description="This pin is used to control the horn relay. AO are Pin 6-7",
        default=7,
        minimum=0,
    )


def export():
    SmallMotorControlConfig.export(
        Path(__file__).parents[2] / "doover_config.json",
        "small_motor_control",
    )
