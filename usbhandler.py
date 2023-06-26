from pymata4 import pymata4
import threading

class USBHandler:
    """
    This class is used to handle the connection to the Arduino board.
    """
    PIN_LED = 13
    PIN_BATTERY = 4
    PIN_LOW_BATTERY = 3
    PIN_RELAY_IN = 7

    def __init__(self, port=None, device_connected_callback=None, arduino_instance_id=1):
        self.device_connected_callback = device_connected_callback
        self.arduino_instance_id = arduino_instance_id
        self.board = None
        self.port = port
        self.device_connected = False

    def connect(self):
        if not self.device_connected:
            self.check_device_thread = threading.Thread(target=self.check_device_connection)
            self.check_device_thread.start()
        
    def cleanup(self):
        if self.board is not None:
            self.board.digital_write(13, 0)
            self.board.shutdown()
            self.device_connected = False

    def check_device_connection(self):
        # while not self.device_connected:
        try:
            # self.board = pymata4.Pymata4()
            if not self.device_connected:
                self.board = pymata4.Pymata4(com_port=self.port, arduino_wait=2, arduino_instance_id=self.arduino_instance_id)
                self.device_connected = True
                self.device_connected_callback(True)
                self.set_pin_modes()
                self.board.digital_write(13, 1)
        except Exception:
            self.device_connected_callback(False)
            self.device_connected = False
            self.board = None

    def set_pin_modes(self):
        self.board.set_pin_mode_digital_output(self.PIN_LED)
        self.board.set_pin_mode_digital_output(self.PIN_BATTERY)
        self.board.set_pin_mode_digital_output(self.PIN_LOW_BATTERY)
        self.board.set_pin_mode_digital_input(self.PIN_RELAY_IN)

    def is_connected(self):
        return self.device_connected