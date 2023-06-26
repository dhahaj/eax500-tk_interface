import json
import os, sys


class Settings:
    """Settings class for the application."""

    def __init__(self, filename="settings.json"):
        """ Initialize the settings class. """
        self.filename = filename

        # Default settings
        self.settings = {
            "serial_port": "COM30",
            "programmer_serial_number": 124512,
            "chip_part": "PIC16F627A",
            "last_user": "dmh",
            "testing_speed": 1.0,
            "auto_test": True,
            "font_family": "Consolas",
            "font_size": 14,
            "font_style": "normal",
            "font_color": "#000000",
            "skip_login": True,
            "debug": True,
        }

        # Load settings from file
        self.load()

    def get(self, key):
        return self.settings.get(key)

    def set(self, key, value):
        self.settings[key] = value

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as file:
                self.settings.update(json.load(file))
        else:
            # Create a settings file from defaults
            with open(os.path.join(".", self.filename), "w") as file:
                json.dump(self.settings, file, indent=4)


    def save(self):
        with open(self.filename, "w") as file:
            json.dump(self.settings, file, indent=4)
