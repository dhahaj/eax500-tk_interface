from eax500 import MainWindow
from settings import Settings
from applogger import AppLogger
from user import User

import tkinter as tk
from tkinter import StringVar
from tkinter.font import Font
from tkinter.ttk import Frame

class Login:
    """
    A class to create a login GUI. The GUI has two entry fields for username and password, and a login button.
    The login button calls the login() method, which checks if the username and password are correct.
    The is_logged_in() method returns True if the user is logged in, and False otherwise.
    """

    def __init__(self):
        """
        Initialize the login GUI Window.
        """
        self.settings = Settings() # Create a settings object
        
        self.app_logger = AppLogger("logger").get_logger() # Create a logger object

        self.users = User()  # Create a user object
        self.users.load_users()  # Load the users from the users.json file

        self.root = tk.Tk() # Create the root window
        self.root.title("Login") # Set the title of the window
        
        self.root.attributes("-topmost", 1) # Make the window always on top

        self.username_label = tk.Label(self.root, text="Username:") # Create a label for the username
        self.password_label = tk.Label(self.root, text="Password:") # Create a label for the password

        self.username_entry = tk.Entry( # Create an entry field for the username
            self.root, textvariable=StringVar(value=self.settings.get("last_user"))
        )
        self.password_entry = tk.Entry(self.root, show="*") # Create an entry field for the password

        self.login_button = tk.Button(self.root, text="Login", command=self.login) # Create a login button
        self.cancel_button = tk.Button(self.root, text="Cancel", command=self.root.destroy) # Create a cancel button

        # Place the widgets in the window
        self.username_label.grid(row=0, column=0, padx=10, pady=10)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        self.password_label.grid(row=1, column=0, padx=10, pady=10)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        self.login_button.grid(row=2, column=0, padx=10, pady=10)
        self.cancel_button.grid(row=2, column=1, padx=10, pady=10)

        # Create a label to display a message if the login fails
        self.failure_label = tk.Label(self.root, text="")
        self.failure_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.login_status = False
        self.user = None
        self.admin = None

        # Bind the Enter and Escape keys 
        self.root.bind("<Return>", lambda event: self.login())
        self.root.bind("<Escape>", lambda event: self.root.destroy())

        # Check if the skip_login setting is set to True. If so, skip the login window
        # and go directly to the main window.
        if self.settings.get("skip_login"):
            self.root.destroy()
            self.main_window = MainWindow()
            self.main_window.run()

    def login(self):
        """
        Check if the username and password are correct.
        """
        username = self.username_entry.get()
        password = self.password_entry.get()

        # if username in self.users and self.users[username] == password:
        if self.users.validate_credentials(username, password):
            self.login_status = True
            self.user = username
            self.root.destroy()
            self.app_logger.info(f"User {self.user} logged in")
            self.settings.set("last_user", self.user)
            self.main_window = MainWindow()
            self.main_window.run()
        else:
            self.app_logger.error(f"Invalid username or password for user {username}")
            self.failure_label.config(text="Invalid username or password.", fg="red")
            self.login_status = False
            self.user = None

    def is_logged_in(self):
        """
        Return the login status.
        """
        return self.login_status

    def run(self):
        """
        Run the login GUI.
        """
        self.root.mainloop
