import json
import os


class Settings:
    """Settings class for the GUI."""

    def __init__(self, filename="settings.json"):
        """
        Initialize the settings class.

        :param filename: The name of the settings file.
        """
        self.filename = filename

        # Default settings
        self.settings = {
            "serial_port": "COM30",
            "programmer_serial_number": "1E660",
            "chip_part": "PIC16F627A",
            "last_user": "dmh",
            "testing_speed": 1.0,
            "auto_test": True,
            "font_family": "Consolas",
            "font_size": 14,
            "font_style": "normal",
            "font_color": "#000000",
            "skip_login": True,
            "arduino_instance_id": 1,
            "debug": True,
        }

        # Load settings from file
        self.load()

    def get(self, key):
        """
        Get a setting.

        :param key: The key of the setting.
        :return: The value of the setting.
        """
        return self.settings.get(key)

    def set(self, key, value):
        """
        Set a setting.

        :param key: The key of the setting.
        :param value: The value of the setting.
        """
        self.settings[key] = value
        self.save()

    def load(self):
        """Load the settings from a JSON file."""
        if not os.path.exists(self.filename):
            # Create a settings file from defaults
            with open(os.path.join(".", self.filename), "w") as file:
                json.dump(self.settings, file, indent=4)
        with open(self.filename, "r") as file:
            self.settings.update(json.load(file))

    def save(self):
        """Save the settings to a JSON file."""
        with open(self.filename, "w") as file:
            json.dump(self.settings, file, indent=4)

    def get_path(self):
        """
        Get the path of the settings file.

        :return: The path of the settings file.
        """
        return os.path.abspath(self.filename)
