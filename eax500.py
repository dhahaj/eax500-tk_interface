import subprocess
import threading
import os
import time
import tkinter
from settings import Settings
from applogger import AppLogger
from usbhandler import USBHandler
from fontchooser import FontChooser
from user import User, SingleUser
from login import Login
from tkfontchooser import askfont

# import tkinter as tk
from tkinter import Tk
from tkinter import (
    Menu,
    Button,
    END,
    Label,
    StringVar,
    messagebox,
    simpledialog,
)
from tkinter.font import Font
from tkinter.ttk import Frame
import tkinter as tk
from manual_window import ManualWindow

app_logger = AppLogger("logger").get_logger()
settings = Settings()
user = User()
logged_in_user = None

# class Login:
#     """
#     A class to create a login GUI. The GUI has two entry fields for username and password, and a login button.
#     The login button calls the login() method, which checks if the username and password are correct.
#     The is_logged_in() method returns True if the user is logged in, and False otherwise.
#     """

#     def __init__(self):
#         """
#         Initialize the login GUI Window.
#         """
#         self.root = tk.Tk()
#         self.users = User()  # Create a user object
#         if settings.get("skip_login"):
#             self.root.destroy()
#             self.main_window = MainWindow()
#             self.main_window.run()
#         else:
#             self.users.load_users()  # Load the users from the users.json file

#         self.root.title("Login")

#         # Make the window always on top
#         self.root.attributes("-topmost", 1)

#         self.username_label = tk.Label(self.root, text="Username:")
#         self.password_label = tk.Label(self.root, text="Password:")

#         self.username_entry = tk.Entry(
#             self.root, textvariable=StringVar(value=settings.get("last_user"))
#         )
#         self.password_entry = tk.Entry(self.root, show="*")

#         self.login_button = tk.Button(self.root, text="Login", command=self.login)
#         self.cancel_button = tk.Button(

#             self.root, text="Cancel", command=self.root.destroy
#         )

#         self.username_label.grid(row=0, column=0, padx=10, pady=10)
#         self.username_entry.grid(row=0, column=1, padx=10, pady=10)
#         self.password_label.grid(row=1, column=0, padx=10, pady=10)
#         self.password_entry.grid(row=1, column=1, padx=10, pady=10)
#         self.login_button.grid(row=2, column=0, padx=10, pady=10)
#         self.cancel_button.grid(row=2, column=1, padx=10, pady=10)

#         self.failure_label = tk.Label(self.root, text="")
#         self.failure_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

#         self.login_status = False
#         self.user = None
#         self.admin = None

#         # Usernames and passwords

#         # Bind the Enter key to the login method
#         self.root.bind("<Return>", lambda event: self.login())

#     def login(self, login=True):
#         """
#         Check if the username and password are correct.

#         :param login: If True, the login button was pressed. If False, the Enter key was pressed.
#         """
#         # if login:
#         #     self.login_status = True
#         #     # self.user = username
#         #     self.root.destroy()
#         #     self.main_window = MainWindow()
#         #     self.main_window.add_text(f"Welcome, {self.user}!")
#         #     self.main_window.run()
#         username = self.username_entry.get()
#         password = self.password_entry.get()
#         # if username in self.users and self.users[username] == password:
#         if self.users.validate_credentials(username, password):
#             self.login_status = True
#             self.user = username
#             self.root.destroy()
#             app_logger.info(f"User {self.user} logged in")
#             settings.set("last_user", self.user)
#             self.main_window = MainWindow()
#             self.main_window.run()
#         else:
#             app_logger.error(f"Invalid username or password for user {username}")
#             self.failure_label.config(text="Invalid username or password.", fg="red")
#             self.login_status = False
#             self.user = None

#     def is_logged_in(self):
#         """
#         Return the login status.
#         """
#         return self.login_status

#     def run(self):
# """
# Run the login GUI.
# """
# self.root.mainloop()


class MainWindow:
    """
    A class to create the main GUI. The GUI has a text box for displaying messages, menu bar,
    a button for testing and programming.
    """

    DEFAULT_TESTING_SPEED = 2000  # Default testing speed in ms

    def __init__(self):
        """
        Initialize the program.
        """
        self.window = tk.Tk()

        app_logger.info("Main window initialized")

        # Get the font from the settings file
        self.font = Font(
            family=settings.get("font_family"),
            size=settings.get("font_size"),
            weight=settings.get("font_style"),
        )

        # Initialize variables
        self.blocked = False
        self.queue = []
        self.device = None
        self.blinker_running = False

        self.blink_thread = threading.Thread(target=self.do_blink, args=(settings.get("indicator_pin"),))
        self.blink_thread.name = "Blink Thread"
        self.blink_thread.daemon = True

        # Setup the GUI components
        self.setup_components()

        # Populate the text area with the testing instructions
        self.load_text_from_file()

        self.dev = None

        if settings.get("skip_login"):
            self.window.withdraw()
            login = Login(window=self.window, settings=settings)
            login.run()

    def setup_components(self):
        """
        Setup the GUI components.
        """
        self.window.geometry("900x700")
        self.window.title("EAX-500 Interface")

        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create frame for the bottom of the window
        self.bottom_frame = Frame(self.window)
        self.bottom_frame.pack(side="bottom", fill="x")

        # Create menu
        self.menu = Menu(self.window)  # Top Menu
        self.window.config(menu=self.menu)  # Add menu to window

        self.device_menu = Menu(self.menu, tearoff=0, font=self.font)  # Top Device Menu

        self.file_menu = Menu(self.menu, tearoff=0, font=self.font)  # Top File Menu
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Logout", command=self.logout)  # Logout
        self.file_menu.add_command(  # Connect to Arduino
            label="Connect",
            command=lambda: self.connect(id=settings.get("arduino_instance_id")),
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_closing)

        self.menu.add_cascade(label="Device", menu=self.device_menu)
        self.device_menu.add_command(
            label="EAX500", command=lambda: self.select_device("EAX500")
        )
        self.device_menu.add_command(
            label="EAX505", command=lambda: self.select_device("EAX505")
        )
        self.device_menu.add_command(
            label="EAX510", command=lambda: self.select_device("EAX510")
        )
        self.device_menu.add_command(
            label="EAX515", command=lambda: self.select_device("EAX515")
        )
        self.device_menu.add_command(
            label="EAX520", command=lambda: self.select_device("EAX520")
        )
        self.device_menu.add_command(
            label="EAX525", command=lambda: self.select_device("EAX525")
        )

        self.settings_menu = Menu(  # Top Settings Menu
            self.menu, tearoff=0, font=self.font
        )

        self.menu.add_cascade(  # Add Settings Menu
            label="Settings", menu=self.settings_menu
        )
        self.settings_menu.add_command(  # Opens the settings file in notepad
            label="Modify Settings", command=self.open_settings
        )
        self.settings_menu.add_command(  # Displays the contents of the settings file in the text area
            label="Show Settings", command=self.show_settings
        )

        self.settings_menu.add_separator(background="red")

        self.settings_menu.add_command(  # Add User
            label="Add User",
            command=lambda: messagebox.showinfo("Add User", "Not implemented yet"),
        )
        self.settings_menu.add_command(  # Remove User
            label="Remove User",
            command=lambda: messagebox.showinfo("Remove User", "Not implemented yet"),
        )
        self.settings_menu.add_command(  # Change Font
            label="Change Font", command=self.get_font  # FontChooser(self.window)
        ),
        self.settings_menu.add_command(  # Change Test Speed
            label="Test Speed",
            command=lambda: self.get_user_input(
                "Test Speed", "Enter Test Speed (%):", "testing_speed", "float"
            ),
        )
        self.settings_menu.add_command(  # Set Auto Login
            label="Auto Login",
            command=lambda: settings.set(
                "skip_login", messagebox.askyesno("Auto Login", "Login automatically?")
            ),
        )
        self.settings_menu.add_command(  # Set Auto Testing
            label="Auto Testing",
            command=lambda: settings.set(
                "auto_test",
                messagebox.askyesno("Auto Testing", "Run test automatically?"),
            ),
        )
        self.settings_menu.add_command(  # Select the chip
            label="Select Chip",
            command=lambda: self.get_user_input(
                "Select Chip", "Enter Chip: ", "chip_part"
            ),
        )
        self.settings_menu.add_command(  # Set the programmer serial number
            label="Programmer Serial Number",
            command=lambda: self.get_user_input(
                "Programmer Serinal Number",
                "Enter Serial Number: ",
                "programmer_serial_number",
            ),
        )
        self.settings_menu.add_command(  # Set the Arduino ID
            label="Arduino ID",
            command=lambda: self.get_user_input(
                "Arduino ID",
                "Enter the Arduino board ID: ",
                "arduino_instance_id",
                "int",
            ),
        )
        self.settings_menu.add_command(
            label="Manual Control",
            command=lambda: self.show_manual_control(),
        )  

        self.help_menu = Menu(self.menu, tearoff=0, font=self.font)  # Top Help Menu
        self.menu.add_cascade(label="Help", menu=self.help_menu)  # Add Help Menu
        self.help_menu.add_command(  # Shows the log file in the text area
            label="Show Log", command=self.show_log
        ) 

        options = [{"font":"parent"}]
        self.help_menu.add_command(  # Shows a dialog with information about the program
            label="About",
            command=lambda: messagebox.showinfo(
                "About",
                "EAX-300/500 Testing Interface\n\nVersion 0.0.1\n\nDesigned by: Daniel Hahaj\nhttps://github.com/dhahaj/eax500-tk_interface.git\nVisit the repository for more information.\n\n©2023 Detex Corporation",
                parent=self.window,
            ),
        )

        self.menu.add_separator()

        self.menu.add_cascade(  # Add an easy way to connect to the fixture
            label="Connect",
            command=lambda: self.connect(id=settings.get("arduino_instance_id")),
        )

        # Create text area
        self.text_area_frame = tk.Frame(self.window)
        self.text_area_frame.pack(fill="both", expand=True)
        self.text_area = tk.Text(
            self.text_area_frame, wrap="word", state="disabled", font=self.font
        )
        self.text_area.pack(
            side="left", fill="both", expand=True, padx=(10, 0), pady=(10, 0)
        )

        # Create Scrollbar
        self.scrollbar = tk.Scrollbar(
            self.text_area_frame, command=self.text_area.yview
        )
        self.scrollbar.pack(side="right", fill="y")

        # Configure the text area to use the scrollbar
        self.text_area.config(yscrollcommand=self.scrollbar.set)

        # Set up selected device
        self.selected_device = StringVar()
        self.selected_device.set("No device selected")

        # Create buttons
        self.button1 = Button(
            self.bottom_frame,
            text="Program",
            height=2,
            width=10,
            font=self.font,
            takefocus=1,
            command=self.program,
            padx=(3),
        )
        self.button1.grid(row=0, column=0, sticky="w")

        # Create label for selected device
        self.device_label = Label(
            self.bottom_frame, textvariable=self.selected_device, font=self.font
        )
        self.device_label.grid(row=0, column=1)

        self.usb_label = Label(
            self.bottom_frame, text="USB: Disconnected", font=self.font
        )
        self.usb_label.config(fg="red")
        self.usb_label.grid(row=0, column=2)

        self.button2 = Button(
            self.bottom_frame,
            text="Test",
            height=2,
            width=10,
            font=self.font,
            command=self.run_test,
            padx=(3),
        )
        self.button2.grid(row=0, column=3, sticky="e")

        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.bottom_frame.grid_columnconfigure(2, weight=1)

    def show_manual_control(self):
        manualwindow = ManualWindow(None, self.dev)

    def device_connected_callback(self, connected):
        """
        Callback function for when the device is connected or disconnected.

        :param connected: True if the device is connected, False otherwise.
        """
        if connected:
            print("Device connected!")
            app_logger.info("Fixture connected.")
            self.dev.write_pin_by_func(pin_function="indicator", value=1)
            self.usb_label.config(fg="green")
            self.usb_label.config(
                text=f"USB Connected: {self.dev.board.serial_port.port}"
            )
            self.add_text("\r\nConnection established.")
            if not self.blink_thread.is_alive():
                self.blink_thread.start()
                self.blinker_running = True
            # self.run_blinker()
        else:
            print("Device disconnected!")
            app_logger.info("Device disconnected.")
            self.usb_label.config(fg="red")
            self.usb_label.config(text="USB: Disconnected")

    def connect(self, id=1):
        """
        Connect to the device.
        """
        if self.dev is None:
            # if not self.dev.is_connected():
            self.add_text("\r\nConnecting to fixture...")
            self.instance_id = id
            self.dev = USBHandler(
                device_connected_callback=self.device_connected_callback,
                arduino_instance_id=id,
                debug=settings.get("debug"),
            )
            self.dev.connect()
        elif not self.dev.is_connected():
            self.dev.connect()
            self.add_text("\r\nConnecting to fixture...")
        else:
            self.add_text("\r\nAlready connected to fixture.")

    def select_device(self, device):
        """
        Select the device to program. This will change the color of the device label.

        :param device: The device to program.
        """
        if not self.blocked:
            app_logger.info(f"Device {device} selected")
            if device == "EAX500" or device == "EAX300":
                self.device_label.config(fg="green")
            else:
                self.device_label.config(fg="red")

            self.selected_device.set(f"Selected device: {device}")
            self.device = device

    def set_user(self, user):
        """
        Set the user.

        :param user: The user.
        """
        app_logger.info(f"User {user} selected")
        self.user = user

    def add_text(self, text):
        """
        Add text to the text area.

        :param text: The text to add.
        """
        # Temporarily make the text widget editable
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(END, text + "\n")
        self.text_area.see(END)
        # Disable the text widget again
        self.text_area.config(state=tk.DISABLED)

    def clear_text(self):
        """
        Clear all text from the text area.
        """
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, END)
        # self.load_text_from_file("instructions.txt")  # Replace with your filename
        self.text_area.config(state=tk.DISABLED)

    def load_text_from_file(self, filename="instructions.txt"):
        """
        Load text from a file and add it to the text area.

        :param filename: The name of the file to load.
        """
        if os.path.exists(filename):
            with open(filename, "r") as file:
                content = file.read()
            self.add_text(content)
        else:
            self.add_text(f"{filename} not found!")

    def logout(self):
        """Logout of the application."""
        # if not self.blocked and not settings.get("skip_login"):
        if self.dev is not None and self.dev.is_connected():
            self.dev.board.write_pin_by_func(pin_function="indicator", value=0)
            self.dev.cleanup()
        self.window.withdraw()
        login = Login(window=self.window ,settings=settings, callback=self.set_user)
        login.run()

    def program(self):
        """Program the device."""
        if not self.blocked and self.device is not None:
            # if not self.blink_thread.is_alive():
            #     self.blink_thread.start()
            self.blinker_running = True
            settings.load()
            firmware = f"firmware/{self.device}_v59.hex"
            chip = settings.get("chip_part")
            serial = settings.get("programmer_serial_number")
            command = ["up.exe", f"/part {chip} /q1 /s {serial} /p {firmware}"]
            thread = threading.Thread(target=self.run_command, args=(command,))
            self.blocked = True
            app_logger.info(f"Programming {self.device} started")
            thread.start()

    def run_command(self, command):
        """
        Run a command in a separate thread.

        :param command: The command to run.
        """
        settings.load()
        process = subprocess.run(command)
        self.blocked = False
        self.blinker_running = False
        if settings.get("auto_test"):
            self.run_test()
        if process.returncode == 0:
            self.add_text("Programming successful.")
            app_logger.info(f"Programming {self.device} successful")
        else:
            self.add_text("Programming failed.")
            app_logger.error(
                f"Programming {self.device} failed. Error code: {process.returncode}"
            )

    def run_test(self):
        """Run the test."""
        if not self.blocked and self.device is not None and self.dev.is_connected():
            self.blinker_running = False
            app_logger.info(f"Testing {self.device} started")
            self.clear_text()
            # Clear the queue
            self.queue = []
            speed = settings.get("testing_speed")

            self.queue.append(  # turn on indicator
                (10, self.dev.write_pin_by_func, "testing indicator", 1)
            )

            self.queue.append(  # Add tasks to the queue
                (100, self.add_text, f"Starting test for {self.device}...")
            )

            self.queue.append(
                (
                    int(self.DEFAULT_TESTING_SPEED * speed),
                    self.add_text,
                    "\nTurning on battery power...",
                )
            )

            self.queue.append(  # turn on battery
                ((10), self.dev.write_pin_by_func, "battery", 1)
            )

            self.queue.append(
                (
                    int(self.DEFAULT_TESTING_SPEED * speed),
                    self.add_text,
                    "Starting low battery test...",
                )
            )

            self.queue.append(  # turn on low battery
                ((10), self.dev.write_pin_by_func, "low battery", 1)
            )

            self.queue.append((int(2000 * speed), self.add_text, "Low battery off."))

            self.queue.append(  # turn off low battery
                ((10), self.dev.write_pin_by_func, "low battery", 0)
            )

            self.queue.append(
                (
                    int(1000 * speed),
                    self.add_text,
                    "Perform the following:\n\t  1. Press the key switch: The siren sounds\n\t  2. Press the cylinder switch: The LEDs turn on",
                )
            )

            self.queue.append((int(5000 * speed), self.add_text, "Testing complete."))

            self.queue.append(  # turn off battery
                ((10), self.dev.write_pin_by_func, "battery", 0)
            )

            self.queue.append((1000, self.clear_text))

            self.queue.append((100, self.load_text_from_file, "instructions.txt"))

            self.queue.append(  # turn off indicator
                ((10), self.dev.write_pin_by_func, "testing indicator", 0)
            )

            self.blocked = True
            # Start processing the queue
            self.process_queue()

        else:
            self.add_text("Cannot run test.")
            app_logger.error(f"Testing {self.device} blocked.")

    def process_queue(self):
        """Process the queue."""
        if self.queue:
            delay, task, *args = self.queue.pop(0)
            self.window.after(delay, lambda: self.execute_task(task, args))
        else:
            self.blocked = False

    def execute_task(self, task, args):
        """
        Execute a task.

        :param task: The task to execute.
        :param args: The arguments to pass to the task.
        """
        task(*args)
        self.process_queue()  # Continue processing the queue

    def open_settings(self):
        """Open the settings file."""
        command = ["notepad.exe", "settings.json"]
        subprocess.Popen(command)

    def show_settings(self):
        """Show the settings in the text area."""
        self.clear_text()  # clear the text area
        settings.load()  # reload the settings
        self.add_text("Settings:\r\n")
        self.add_text("Settings file: settings.json")
        self.add_text(f"Settings file location: {settings.get_path()}")
        self.add_text("\r\n")
        self.add_text(f"Serial Port: {settings.get('serial_port')}")
        self.add_text(
            f"Programmer serial number: {settings.get('programmer_serial_number')}"
        )
        self.add_text(f"Chip part: {settings.get('chip_part')}")
        self.add_text(f"Auto test: {settings.get('auto_test')}")
        self.add_text(f"Testing speed: {settings.get('testing_speed')}")
        self.add_text(
            f"Font: {settings.get('font_family')}, {settings.get('font_size')}, {settings.get('font_style')}"
        )
        self.add_text(f"Arduino Instance ID: {settings.get('arduino_instance_id')}")
        self.add_text(f"Skip Login: {settings.get('skip_login')}")
        self.add_text(f"Debug: {settings.get('debug')}")

    def get_font(self):
        """Get the font."""
        _font = settings.get("font_family")
        _size = settings.get("font_size")
        _style = settings.get("font_style")
        # current_font = Font(
        font_dict = {"family": _font, "size": int(_size), "weight": _style}
        fc = askfont(self.window, **font_dict)
        # fc = FontChooser(master=self.window) #, **font_dict)
        # fc.mainloop()
        # self.new_font = askfont(self.window, **current_font)#, title="Select Font", command=self.set_font)
        print(fc)
        self.set_font(fc)
        # return new_font

    def set_font(self, font):
        """Set the font."""
        settings.set("font_family", font["family"])
        settings.set("font_size", font["size"])
        settings.set("font_style", font["weight"])
        print(
            settings.get("font_family"),
            settings.get("font_size"),
            settings.get("font_style"),
        )
        self.font = Font(
            family=settings.get("font_family"),
            size=settings.get("font_size"),
            weight=settings.get("font_style"),
        )
        self.reload_window()
        self.show_settings()

    def show_log(self):
        """Show the logs in the text area."""
        self.clear_text()
        self.add_text("Logs:\r\n")
        self.add_text(AppLogger.get_logs())

    def get_user_input(self, title, prompt, key, type=None):
        """
        Get user input.

        :param title: The title of the dialog box.
        :param prompt: The prompt to display.
        :param key: The key to store the value in.
        :param type: The type of the value.
        """
        self.window.withdraw()  # hide the main window

        initialvalue = settings.get(key)

        if type == "int":
            user_input = simpledialog.askinteger(
                title=title, prompt=prompt, initialvalue=initialvalue
            )
        elif type == "float":
            user_input = simpledialog.askfloat(
                title=title, prompt=prompt, initialvalue=initialvalue
            )
        else:
            user_input = simpledialog.askstring(
                title=title, prompt=prompt, initialvalue=initialvalue
            )

        if user_input is not None:
            settings.set(key, user_input)
            print(user_input)
            settings.save()
        self.window.deiconify()  # show the main window

    def on_closing(self):
        """Handle the window closing."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.dev != None and self.dev.is_connected():
                self.dev.cleanup()
            self.window.destroy()

    def do_blink(self, pin):
        """Blink the indicator light."""
        value = not self.dev.read_pin(pin)
        while True:
            while self.blinker_running:
                self.dev.write_pin_by_func("indicator", value)
                value = not value
                time.sleep(0.1)

    def reload_window(self):
        """Reload the window."""
        self.button2 = Button(
            self.bottom_frame,
            text="Test",
            height=2,
            width=10,
            font=self.font,
            command=self.run_test,
            padx=(3),
        )
        # self.window.destroy()
        # self.window = tk.Tk()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    main = MainWindow()
    main.run()
