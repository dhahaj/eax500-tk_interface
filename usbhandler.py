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
        debug=False,
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
        self.debug = debug

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
        if not self.device_connected and self.board is None:
            self.check_device_thread = threading.Thread(
                target=self.check_device_connection
            )
            self.check_device_thread.start()
            if self.debug:
                print(f"Method: {self.connect.__name__} - Thread started")

    def cleanup(self):
        """Cleanup the Arduino board."""
        if self.board is not None:
            if self.debug:
                print(f"Method: {self.cleanup.__name__}")
            self.board.digital_write(13, 0)
            self.board.shutdown()
            self.device_connected = False

    def check_device_connection(self):
        """Check the connection to the Arduino board."""
        try:
            if self.debug:
                print(f"Method: {self.check_device_connection.__name__}, Connection: {self.device_connected}")
            if not self.device_connected:
                self.board = pymata4.Pymata4(  # Create a new Pymata4 instance
                    com_port=self.port,
                    arduino_wait=2,
                    arduino_instance_id=self.arduino_instance_id,
                )
                self.load_pins()  # Load the pins from the pins.json file
                self.set_pin_modes()  # Set the pin modes
                pin = self.get_pin_by_function("indicator")
                if self.debug:
                    print(pin)

                self.device_connected = True  # Set the device connected flag
                if self.device_connected_callback is not None:
                    self.device_connected_callback(True)  # Call the callback function
        except Exception as e:
            print(f"Exception occurred while connecting to device: {e}")
            traceback.print_exc()
            if self.device_connected_callback is not None:
                self.device_connected_callback(False)
            self.device_connected = False
            self.board = None

    def get_pin_by_function(self, function):
        """
        Fetch a pin by its function.

        :param pins: List of pin dictionaries.
        :param function: The function to search for.
        :return: The integer pin number, or None if not found.
        """
        for pin in self.pins:
            # print(pin)
            if pin["function"] == function:
                return pin['pin_number']
        if self.debug:
            print(f"Pin with function {function} not found.")
        return None  # If no pin with the function is found, return None

    def set_pin_modes(self):
        """Set the pin modes for the Arduino board."""
        if self.debug:
            print(f"Method: {self.set_pin_modes.__name__}")
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
        if self.debug:
            print(f"Method: {self.load_pins.__name__}")
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
        if self.debug:  
            print(f"Method: {self.write_pin.__name__}, Pin: {pin_number}, Value: {value}")
        
        if pin_number is not None: # If the pin is found
            _pin = int(pin_number)

        self.board.digital_write(_pin, value)
            # print(f"Pin with number {pin_number} not found.")

    def write_pin_by_func(self, pin_function, value):
        """
        Write a value to a pin by its function.

        :param pin_function: The function of the pin.
        :param value: The value to write to the pin.
        """
        if self.debug:
            print(f"Method: {self.write_pin_by_func.__name__}, Pin: {pin_function}, Value: {value}")
        if pin_function is not None: # If the pin function is specified
            pin = self.get_pin_by_function(pin_function)
            if pin is not None: # If the pin is found
                self.board.digital_write(pin, value)
            else:
                print(f"Pin with function {pin_function} not found.")
        else:
            print("Pin function not specified.")

    def read_pin(self, pin_number):
        """
        Read the value of a pin by its number.

        :param pin_number: The pin number to read from.
        :return: The value of the pin.
        """
        if self.debug:
            print(f"Method: {self.read_pin.__name__}, Pin: {pin_number}")
        if self.is_connected() and pin_number is not None:
            if isinstance(pin_number, str):
                pin = int(pin_number)
            else:
                pin =pin_number
            return self.board.digital_read(pin)[0]
        else:
            if self.debug:
                if not self.is_connected():
                    print("Device not connected.")
                if pin_number is None:
                    print("Pin number not specified.")
            return None