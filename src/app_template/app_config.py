from pathlib import Path

from pydoover import config


class SampleConfig(config.Schema):
    def __init__(self):
        # these 2 are device specific, and inherit from the device-set variables.
        # However, the user can override them if they wish.

        self.num_di = config.Integer(
            "Digital Input Count",
            default=config.Variable("device", "digitalInputCount"),
            minimum=0,
        )
        self.num_do = config.Integer(
            "Digital Output Count",
            default=config.Variable("device", "digitalOutputCount"),
            minimum=0,
        )

        self.outputs_enabled = config.Boolean("Digital Outputs Enabled", default=True)
        self.funny_message = config.String("A Funny Message")  # this will be required as no default given.

        self.sim_app_key = config.Application("Simulator App Key", description="The app key for the simulator")


if __name__ == "__main__":
    SampleConfig().export(Path(__file__).parent.parent.parent / "doover_config.json", "sample_application")
