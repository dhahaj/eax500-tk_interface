from pymata4 import pymata4

class USBHandler:
    def __init__(self, port=None):
        self.board = None
        self.port = port

    def connect(self):
        self.board = pymata4.Pymata4(com_port=self.port)
        self.board.set_pin_mode_digital_output(13)
        self.board.digital_write(13, 1)

    def cleanup(self):
        self.board.shutdown()
