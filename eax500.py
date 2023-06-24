import subprocess
import threading

import tkinter as tk
from tkinter import Menu, Text, Button, END

class Login:
    """
    A class to create a login GUI. The GUI has two entry fields for username and password, and a login button.
    The login button calls the login() method, which checks if the username and password are correct.
    The is_logged_in() method returns True if the user is logged in, and False otherwise.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login")

        # Make the window always on top
        self.root.attributes('-topmost', 1)

        self.username_label = tk.Label(self.root, text="Username:")
        self.password_label = tk.Label(self.root, text="Password:")

        self.username_entry = tk.Entry(self.root)
        self.password_entry = tk.Entry(self.root, show="*")

        self.login_button = tk.Button(self.root, text="Login", command=self.login)
        self.cancel_button = tk.Button(self.root, text="Cancel", command=self.root.destroy)

        self.username_label.grid(row=0, column=0, padx=10, pady=10)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        self.password_label.grid(row=1, column=0, padx=10, pady=10)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        self.login_button.grid(row=2, column=0, padx=10, pady=10)
        self.cancel_button.grid(row=2, column=1, padx=10, pady=10)

        self.failure_label = tk.Label(self.root, text="")
        self.failure_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.login_status = False
        self.user = None
        self.admin = None

        # Usernames and passwords
        self.users = {
            "admin": "password",
            "dmh": "d853",
            "sm": "1234"
        }

        # Bind the Enter key to the login method
        self.root.bind('<Return>', lambda event: self.login())

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username in self.users and self.users[username] == password:
            self.login_status = True
            self.user = username
            self.root.destroy()
            self.main_window = MainWindow()
            self.main_window.add_text(f"Welcome, {self.user}!")
            self.main_window.run()
        else:
            # print("Invalid username or password.")
            self.failure_label.config(text="Invalid username or password.", fg="red")
            self.login_status = False
            self.user = None

    def is_logged_in(self):
        return self.login_status

    def run(self):
        self.root.mainloop()

class MainWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.geometry("800x600")
        self.window.title("Main Window")

        self.queue = []

        # Create menu
        self.menu = Menu(self.window)
        self.window.config(menu=self.menu)

        self.file_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='Logout', command=self.logout)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', command=self.window.destroy)

        self.device_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='Device', menu=self.device_menu)

        # Create text area
        self.text_area = Text(self.window, wrap="word", state="disabled", font=("Times New Roman", 12))
        self.text_area.pack(expand=True, fill='both')

        # Create buttons
        self.button1 = Button(self.window, text="Program", height=2, width=10, font=("Times New Roman", 12), takefocus=1, command=self.program)
        self.button1.pack(side="left", padx=(10, 0))

        self.button2 = Button(self.window, text="Test", height=2, width=10, font=("Times New Roman", 12), command=self.run_test)
        self.button2.pack(side="right", padx=(0, 10))

        self.load_text_from_file()

    def set_user(self, user):
        self.user = user

    def add_text(self, text):
        # Temporarily make the text widget editable
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(END, text + "\n")
        # Disable the text widget again
        self.text_area.config(state=tk.DISABLED)

    def clear_text(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, END)
        # self.load_text_from_file("instructions.txt")  # Replace with your filename
        self.text_area.config(state=tk.DISABLED)

    def load_text_from_file(self, filename="instructions.txt"):
        with open(filename, "r") as file:
            content = file.read()
        self.add_text(content)

    def logout(self):
        self.window.destroy()
        login = Login()
        login.run()

    def program(self):
        command = ["cmd", "/c", "up.exe"]
        thread = threading.Thread(target=self.run_command, args=(command,))
        thread.start()

    def run_command(self, command):
        process = subprocess.run(command)
        print(f"The command returned: {process.returncode}")

    def run_test(self):
        self.clear_text()
        # Clear the queue
        self.queue = []
        # Add tasks to the queue
        self.queue.append((1000, self.clear_text))
        self.queue.append((1000, self.add_text, "Starting test for EAX-500"))
        self.queue.append((2000, self.add_text, "\nTurning on battery power..."))
        self.queue.append((2000, self.add_text, "Starting low battery test..."))
        self.queue.append((2000, self.add_text, "Low battery off."))
        self.queue.append((2000, self.add_text, "Testing complete."))
        self.queue.append((2000, self.clear_text))
        self.queue.append((2000, self.load_text_from_file, "instructions.txt"))
        # Start processing the queue
        self.process_queue()

    def process_queue(self):
        if self.queue:
            delay, task, *args = self.queue.pop(0)
            self.window.after(delay, lambda: self.execute_task(task, args))

    def execute_task(self, task, args):
        task(*args)
        self.process_queue()  # Continue processing the queue

    def run(self):
        self.window.mainloop()


# Instantiate and run the Login window
login = Login()
login.run()
