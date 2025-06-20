"""
Basic tests for an application.

This ensures all modules are importable and that the config is valid.
"""

def test_import_app():
    from small_motor_control.application import SmallMotorControlApplication
    assert SmallMotorControlApplication

def test_config():
    from small_motor_control.app_config import SmallMotorControlConfig

    config = SmallMotorControlConfig()
    assert isinstance(config.to_dict(), dict)

def test_ui():
    from small_motor_control.app_ui import SmallMotorControlUI
    assert SmallMotorControlUI

def test_state():
    from small_motor_control.app_state import SmallMotorControlState
    assert SmallMotorControlState