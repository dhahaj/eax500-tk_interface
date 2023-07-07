from login import Login
from eax500 import MainWindow
from settings import Settings
from applogger import AppLogger
from user import User
from usbhandler import USBHandler


if __name__ == "__main__":
    """
    The main function for the EAX500 application. It loads the settings, instantiates the system logger,
    loads the users, and starts the login process. If the login is successful, or if the settings indicate
    to skip the login, the main window is created and the main loop is started. The USB connection then attempts
    to create a connection with the EAX500 fixture.
    """
    settings = Settings("settings.json")  # Create a settings object
    settings.load()  # Load the settings from the settings.json file

    app_logger = AppLogger("logger").get_logger()  # Create a logger object
    app_logger.info(
        "Starting the EAX500 application."
    )  # Log the start of the application

    users = User("users.json")  # Create a user object
    users.load()  # Load the users from the users.json file

    # if skip login is false, create a login window
    if not settings.get("skip_login"):
        login = Login()
        while not login.is_logged_in():
            login.run()
        user = login.get_user()
        app_logger.info(f"User {user['username']} logged in.")
    else:
        user = None

    main_window = MainWindow()  # Create a main window object
    main_window.window.mainloop()  # Start the main loop

    # Create a USBHandler object
    usb_handler = USBHandler(
        arduino_instance_id=settings.get("arduino_instance_id"), # Provide the Arduino instance ID for this particular EAX500 fixture
        device_connected_callback=main_window.device_connected_callback, # Set a callback function for the device
    )
    usb_handler.connect()  # Attempt to connect to the EAX500 fixture

    app_logger.info("Closing the EAX500 application.")
    # usb_handler = USBHandler()

