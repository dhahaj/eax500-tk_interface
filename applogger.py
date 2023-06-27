import os
import shutil
import logging
import zipfile
from datetime import datetime


class AppLogger:
    """
    Logger class

    This class is used to handle the logging system. It creates a logger object
    and adds a file handler and a console handler to it. The file handler is
    used to log all messages to a file and the console handler is used to log
    only error messages to the console.

    The logger object can be retrieved using the get_logger() method. The
    shutdown() method should be called when the program is exiting to close
    the logger object.

    The get_logs() method can be used to get the contents of the log file.
    """

    def __init__(self, name, file_name="debug.log"):
        """
        Initialize the AppLogger class.

        :param name: The name of the logger.
        :param file_name: The name of the log file.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.file_name = file_name

        # Create file handler
        # self.check_and_move_old_log_file()
        file_handler = logging.FileHandler(file_name)
        file_handler.setLevel(logging.DEBUG)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)

        # Create formatters and add it to handlers
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)

        # Add the handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        """
        Return the logger object.

        :return: The logger object.
        """
        return self.logger

    @staticmethod
    def get_logs():
        """
        Get the log file contents.

        :return: The log file contents.
        """
        with open("debug.log", "r") as file:
            return file.read()

    @staticmethod
    def shutdown():
        """
        Shutdown the logging system.
        """
        logging.shutdown()

    def check_and_move_old_log_file(self):
        """
        Check if the log file exists and if it does, check the date of the file.
        If the date of the file is not today, move the file to a new file with the date appended to the file name.
        """
        if os.path.exists(self.file_name):
            file_date = datetime.fromtimestamp(os.path.getmtime(self.file_name))
            print(file_date)

            today = datetime.now()

            if file_date.date() != today.date():
                if not os.path.exists("logs"):
                    os.makedirs("logs")

                new_file_name = f"logs/{self.file_name.split('.')[0]}_{file_date.strftime('%Y-%m-%d')}.log"
                shutil.move(self.file_name, new_file_name)

    @staticmethod
    def archive_logs(archive_name="logs"):
        """
        Archive all log files into a zip archive

        archive_name: The name of the zip archive (without extension, defaults to 'logs')
        """
        shutil.make_archive(archive_name, "zip", "logs")

    @staticmethod
    def add_to_archive(archive_name, file_name):
        """
        Add a file to an existing zip archive

        archive_name: The name of the zip archive (without path or extension)
        file_name: The name of the file to add
        """
        with zipfile.ZipFile(archive_name, "a") as myzip:
            myzip.write(file_name)
