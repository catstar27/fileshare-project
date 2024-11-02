import bcrypt
import csv

"""
### Authentication Class ###

This class handles creation of new users and authentication of existing users.
After checking the given password with the saved passwords, it will return:
0 - Password matched.
1 - Incorrect password.
2 - User not found.
 
### Requirements ###

bcrypt library: pip install bcrypt

"""


class Authentication:
    def __init__(self):
        pass

    # Add user and hashed password to csv file
    def add_user(self, username, password):
        hashed = self.hash_password(password)
        data = [username, hashed]
        with open("user_passwords.csv", "a", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(data)

    # Hash password and convert to string
    def hash_password(self, password):
        bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hash_password = bcrypt.hashpw(bytes, salt)
        string_password = hash_password.decode("utf-8")
        return string_password

    # Read CSV file and check for a match between username and password
    def check_password(self, username, password):
        LOGIN_SUCCESSFUL = 0
        INCORRECT_PASSWORD = 1
        USER_NOT_FOUND = 2

        with open("user_passwords.csv", "r+") as csvfile:
            csv_reader = csv.reader(csvfile)
            bytes = password.encode("utf-8")
            for row in csv_reader:
                hash_password = row[1].encode("utf-8")
                password_matched = bcrypt.checkpw(bytes, hash_password)

                if row[0] == username and not password_matched:
                    return INCORRECT_PASSWORD
                elif row[0] == username and password_matched:
                    return LOGIN_SUCCESSFUL
        return USER_NOT_FOUND