import json
import os

class User:
    """
    This class is used to handle the user data.
    """
    def __init__(self, filename="users.json"):
        """
        Initialize the User class.

        :param filename: The name of the file to store the user data.
        """
        self.board_count = 0
        # Default users
        self.users = [
            {
                "username": "dmh",
                "password": "d853",
                "admin": True
            },
            {
                "username": "sm",
                "password": "1234",
                "admin": True
            },
            {
                "username": "admin",
                "password": "password",
                "admin": True
            }
        ]

        self.filename = filename
        self.users = self.load(self.filename)

    def load(self, filename=None):
        """
        Load the users from a JSON file.

        :param filename: The filename to load the users from.
        """
        if filename is None:
            filename = self.filename
        
        # Check if the file exists
        if os.path.exists(filename):
            # Load settings from file
            with open(filename, "r") as file:
                try:
                    data = json.load(file)
                    if isinstance(data, list):
                        self.users = data
                    else:
                        print("Invalid format in user file. Expected a list.")
                        self.users = []
                except json.JSONDecodeError:
                    print("Failed to decode JSON from user file.")
                    self.users = []
        else: # File does not exist
            print(f"User file {filename} does not exist.")
            self.users = []
        if self.users is None:
            print("No users loaded. self.users is None.")
        elif isinstance(self.users, list):
            print(f"{len(self.users)} users loaded.")
        else:
            print("Unexpected error in load_users(). self.users is not a list.")
        
    def save_users(self):
        """ Save the users to a JSON file. """
        with open(self.filename, 'w') as file:
            json.dump(self.users, file, indent=4)

    def validate_credentials(self, username, password):
        """
        Validate the user credentials.

        :param username: The username to validate.
        :param password: The password to validate.
        :return: True if the credentials are valid, False otherwise.
        """
        for user in self.users:
            print(f"Checking credentials for user: {user['username']} with password: {user['password']}")
            if user['username'] == username and user['password'] == password:
                print(f"Credentials match for user: {username}")
                return True
        print(f"No matching credentials found for user: {username}")
        return False

    def add_user(self, username, password, admin=False):
        """
        Add a user to the user list.
        
        :param username: The username to add.
        :param password: The password to add.
        :param admin: True if the user is an admin, False otherwise.
        :return: True if the user was added, False otherwise.
        """
        # Check if the user already exists
        for user in self.users:
            if user['username'] == username:
                print(f"User {username} already exists.")
                return False
        self.users[username] = {'password': password}
        self.save_users()
        return True

    def remove_user(self, username):
        """
        Remove a user from the user list.
        
        :param username: The username to remove.
        :return: True if the user was removed, False otherwise.
        """
        if username in self.users:
            del self.users[username]
            self.save_users()
            return True
        else:
            print(f"User {username} does not exist.")
            return False

    def is_admin(self, username):
        """
        Check if a user is an admin.

        :param username: The username to check.
        :return: True if the user is an admin, False otherwise.
        """
        if username in self.users:
            return self.users[username]['admin']
        else:
            return False
        
    def get_users(self):
        """
        Get a list of all users.

        :return: A list of all users.
        """
        return [user['username'] for user in self.users]
    
    def get_user(self, username):
        """
        Get a single user.

        :param username: The username to get.
        :return: The user if it exists, None otherwise.
        """
        for user in self.users:
            if user['username'] == username:
                return user
        return None

    @staticmethod
    def make_user(username, password, admin):
        return SingleUser(username, password, admin)
    
    def print_users(self):
        """
        Print all users.
        """
        for user in self.users:
            print(user)



class SingleUser:
    """
    This class defines a single user.
    """
    def __init__(self, username, password, admin=False):
        """
        Initialize the User class.

        :param username: The username of the user.
        :param password: The password of the user.
        :param admin: True if the user is an admin, False otherwise.
        """
        self.username = username
        self.password = password
        self.admin = admin

    def __str__(self):
        return f"User: {self.username}, Admin: {self.admin}"
    
    def is_admin(self):
        """
        Check if the user is an admin.

        :return: True if the user is an admin, False otherwise.
        """
        return self.admin
    
    def check_password(self, password):
        """
        Check if the password matches the user's password.

        :param password: The password to check.
        :return: True if the password matches, False otherwise.
        """
        return self.password == password