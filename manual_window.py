import tkinter as tk
from tkinter import messagebox
# from eax500 import MainWindow
from usbhandler import USBHandler


class ManualWindow(tk.Frame):
    """
    This class is used to create a manual window for the user to interact with the system.
    """

    def __init__(self, master=None, usb_handler=None):
        """
        Initialize the ManualWindow class.

        :param master: The parent widget.
        :param usb_handler: The USBHandler instance to use.
        """
        super().__init__(master)
        if master is None:
            master = tk.Tk()
            master.geometry("300x550")

        self.master = master
        self.pack()

        self.create_widgets()

        if usb_handler is None:
            self.usb_handler = USBHandler()
        else:
            self.usb_handler = usb_handler

        self.usb_handler.connect()

    def create_widgets(self):
        read_button = tk.Button(
            self.master, text="battery", command=self.read_io, width=20, height=4
        )
        read_button.pack(pady=20)

        write_button = tk.Button(
            self.master, text="low battery", command=self.write_io, width=20, height=4
        )
        write_button.pack(pady=20)

        read_button = tk.Button(
            self.master,
            text="testing indicator",
            command=self.read_io,
            width=20,
            height=4,
        )
        read_button.pack(pady=20)

        write_button = tk.Button(
            self.master, text="indicator", command=self.write_io, width=20, height=4
        )
        write_button.pack(pady=20)

    def read_io(self):  # add self as a parameter
        # Implement your IO read operation here
        # messagebox.showinfo("Info", "Read from IO")
        # pin = self.usb_handler.get_pin_by_function("indicator")
        self.usb_handler.read_pin(13)

    def write_io(self):  # add self as a parameter
        # Implement your IO write operation here
        # messagebox.showinfo("Info", "Written to IO")
        # pin = self.usb_handler.get_pin_by_function("indicator")
        self.usb_handler.write_pin(13, not self.usb_handler.read_pin(13))
        # self.usb_handler.write_pin("indicator", not self.usb_handler.read_pin("indicator"))

    def run(self):
        """
        Run the mainloop of the window.
        """
        self.master.mainloop()


# app = ManualWindow(master=tk.Tk())
# app.mainloop()