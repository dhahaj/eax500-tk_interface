from login import Login
from eax500 import MainWindow
from settings import Settings


class Application:
    """
    This class is used to handle the application state.
    """
    def __init__(self):
        self.settings = Settings()
        self.main_window = MainWindow()
        self.login_window = Login(window=self.main_window, settings=self.settings)
        self.user = None
        self.state = "Logged Out"

        if self.settings.get("skip_login"):
            self.transition_to_main()

    def transition_to_login(self):
        # handle transition to login state
        self.state = "Logging In"

    def transition_to_main(self):
        # handle transition to main window state
        self.state = "Logged In"
        self.main_window.run()

    def transition_to_logout(self):
        # handle transition to logout state
        self.state = "Logged Out"

    def transition_to_exit(self):
        # handle transition to exit state
        self.state = "Exiting"

    def get_state(self):
        # return the current state
        return self.state

    def run(self):
        # main application loop
        pass