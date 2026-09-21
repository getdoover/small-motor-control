from pydoover import notifications


class SmallMotorControlNotifications(notifications.Notifications):
    """Notifications this app can send.

    Declaring them publishes a schema with the app, which is what lets an
    operator turn this notification off for themselves without also losing
    every other notification from the device.
    """

    engine_problem = notifications.Notification(
        # Overridden on every send with the reason the engine faulted; this is
        # the fallback wording and what the site shows in the picker.
        "The engine failed to start or stopped unexpectedly",
        display_name="Engine problem",
        description=(
            "Sent when the engine fails to crank within the start window, or "
            "stops while it was meant to be running."
        ),
        severity=notifications.NotificationSeverity.Warn,
    )


def export():
    from pathlib import Path

    SmallMotorControlNotifications.export(
        Path(__file__).parents[2] / "doover_config.json", "small_motor_control"
    )
