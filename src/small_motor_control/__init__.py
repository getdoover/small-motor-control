from pydoover.docker import run_app

from .application import SmallMotorControlApplication


def main():
    """
    Run the application.
    """
    run_app(SmallMotorControlApplication())
