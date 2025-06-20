from pydoover.docker import run_app

from .application import SmallMotorControlApplication
from .app_config import SmallMotorControlConfig

def main():
    """
    Run the application.
    """
    run_app(SmallMotorControlApplication(config=SmallMotorControlConfig()))
