from pymata4 import pymata4
from pymata_express import pymata_express
from applogger import AppLogger
import threading
import json
import os
import asyncio
import time
import traceback
import logging


class USBHandler:
    """
    This class is used to handle the connection to the Arduino board.
    """

    PIN_LOW_BATTERY = 2
    PIN_TESTING_INDICATOR = 4
    PIN_BATTERY = 12
    PIN_INDICATOR = 13

    def __init__(
        self,
        port=None,
        device_connected_callback=None,
        arduino_instance_id=1,
    ):
        """
        Initialize the USBHandler class.

        :param port: The port to connect to.
        :param device_connected_callback: The callback function to call when the device is connected.
        :param arduino_instance_id: The instance ID of the Arduino board.
        """
        self.device_connected_callback = device_connected_callback
        self.arduino_instance_id = arduino_instance_id
        self.board = None
        self.port = port
        self.device_connected = False

        # Default settings
        self.pins = [
            {
                "pin_number": self.PIN_LOW_BATTERY,
                "function": "LOW BATTERY",
                "io_mode": "OUTPUT",
                "pullup_enabled": False,
            },
            {
                "pin_number": self.PIN_TESTING_INDICATOR,
                "function": "TESTING INDICATOR",
                "io_mode": "OUTPUT",
                "pullup_enabled": False,
            },
            {
                "pin_number": self.PIN_BATTERY,
                "function": "BATTERY",
                "io_mode": "OUTPUT",
                "pullup_enabled": False,
            },
            {
                "pin_number": self.PIN_INDICATOR,
                "function": "INDICATOR",
                "io_mode": "OUTPUT",
                "pullup_enabled": False,
            },
        ]

    def connect(self):
        """Connect to the Arduino board."""
        if not self.device_connected:
            self.check_device_thread = threading.Thread(
                target=self.check_device_connection
            )
            self.check_device_thread.start()

    def cleanup(self):
        """Cleanup the Arduino board."""
        if self.board is not None:
            self.board.digital_write(13, 0)
            self.board.shutdown()
            self.device_connected = False

    def check_device_connection(self):
        """Check the connection to the Arduino board."""
        try:
            # self.board = pymata4.Pymata4()
            if not self.device_connected:
                self.board = pymata4.Pymata4(  # Create a new Pymata4 instance
                    com_port=self.port,
                    arduino_wait=2,
                    arduino_instance_id=self.arduino_instance_id,
                )
                self.load_pins()  # Load the pins from the pins.json file
                self.set_pin_modes()  # Set the pin modes
                pin = self.get_pin_by_function("indicator")
                print(pin)
                # self.board.digital_pin_write(pin=self.get_pin_by_function("INDICATOR"), value=1)

                self.device_connected = True  # Set the device connected flag
                self.device_connected_callback(True)  # Call the callback function
        except Exception as e:
            print(f"Exception occurred while connecting to device: {e}")
            traceback.print_exc()
            self.device_connected_callback(False)
            self.device_connected = False
            self.board = None

    def get_pin_by_function(self, function):
        """
        Fetch a pin by its function.

        :param pins: List of pin dictionaries.
        :param function: The function to search for.
        :return: The pin dictionary, or None if not found.
        """
        for pin in self.pins:
            print(pin)
            if pin["function"] == function:
                return pin
        print(f"Pin with function {function} not found.")
        return None  # If no pin with the function is found, return None

    def set_pin_modes(self):
        """Set the pin modes for the Arduino board."""
        print(self.pins)
        for pin in self.pins:
            if pin["io_mode"] == "output":
                self.board.set_pin_mode_digital_output(pin["pin_number"])
            elif pin["io_mode"] == "input":
                self.board.set_pin_mode_digital_input(pin["pin_number"])
                if pin["pullup_enabled"]:
                    self.board.set_pin_mode_digital_input_pullup(pin["pin_number"])

    def is_connected(self):
        """Check if the Arduino board is connected."""
        return self.device_connected

    def load_pins(self, filename="pins.json"):
        """
        Load the pins from a JSON file.

        :param filename: The filename to load the pins from.
        """
        if not os.path.exists(filename):
            # Create a pins.json file from defaults
            with open(os.path.join(".", filename), "w") as file:
                json.dump({"pins": self.pins}, file, indent=4)

        # Load settings from file
        with open(filename, "r") as file:
            self.pins = json.load(file)["pins"]

    def write_pin(self, pin_number, value):
        """
        Write a value to a pin by its number.

        :param pin_number: The pin number to write to.
        :param value: The value to write to the pin.
        """
        if pin_number is not None: # If the pin is found
            _pin = int(pin_number)
            self.board.digital_write(_pin, value)
        else:
            print(f"Pin with number {pin_number} not found.")

    def write_pin(self, pin_function, value):
        """
        Write a value to a pin by its function.

        :param pin_function: The function of the pin.
        :param value: The value to write to the pin.
        """
        if pin_function is not None: # If the pin function is specified
            pin = self.get_pin_by_function(pin_function)
            if pin is not None: # If the pin is found
                self.board.digital_write(pin["pin_number"], value)
            else:
                print(f"Pin with function {pin_function} not found.")
        else:
            print("Pin function not specified.")
