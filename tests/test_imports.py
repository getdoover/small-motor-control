"""
Basic tests for an application.

This ensures all modules are importable and that the config is valid.
"""

def test_import_app():
    from small_motor_control.application import SmallMotorControlApplication
    assert SmallMotorControlApplication

def test_config():
    from small_motor_control.app_config import SmallMotorControlConfig

    assert isinstance(SmallMotorControlConfig.to_schema(), dict)

def test_ui():
    from small_motor_control.app_ui import SmallMotorControlUI
    assert SmallMotorControlUI

def test_tags():
    from small_motor_control.app_tags import SmallMotorControlTags
    assert SmallMotorControlTags

def test_state():
    from small_motor_control.app_state import SmallMotorControlState
    assert SmallMotorControlState
