import os
import socket
import threading
import atexit
from authentication import Authentication


class FileOperator:
    """
    This class handles file operations by storing a working directory.
    To be used on the server side only, not on client.
    This uses threading to handle multiple connections. Only use one instance of this class.
    """
    ip_server = socket.gethostbyname_ex(socket.gethostname())[2][0]
    port = 4450
    buffer = 1024
    format = "utf-8"
    storage_dir = ""
    server = None
    files_open = {}
    auth = Authentication()

    def __init__(self, _storage_dir):
        if os.path.isdir(os.path.abspath(_storage_dir)):
            self.storage_dir = os.path.abspath(_storage_dir)
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.ip_server, self.port))
            self.server_listen()
        else:
            print("Invalid Directory")

    def server_listen(self):
        print(f"Server Listening on {self.ip_server}")
        self.server.listen()
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=[conn, addr])
            thread.start()

    def handle_client(self, conn, addr):
        print(f"Handling Connection at {addr}")
        while True:
            cmd = conn.recv(self.buffer).decode(self.format)
            cmd = cmd.split(' ', 1)
            if len(cmd) == 1:
                cmd.append('')
            if cmd[0] == "send_to_client":
                self.send_to_client(conn, cmd[1])
                break
            elif cmd[0] == "recv_from_client":
                self.recv_from_client(conn, cmd[1])
                break
            elif cmd[0] == "show_dir":
                self.show_dir(conn, cmd[1])
                break
            elif cmd[0] == "delete_server_file":
                self.delete_file(conn, cmd[1])
                break
            elif cmd[0] == "create_subfolder":
                self.create_subfolder(conn, cmd[1])
                break
            elif cmd[0] == "close_connection":
                break
            elif cmd[0] == "login":
                self.check_user(conn, cmd[1])
            elif cmd[0] == "adduser":
                self.add_user(conn, cmd[1])
            else:
                break
        conn.close()

    def send_to_client(self, client_socket, filename):  # Sends a file to the client
        print(f"Sending File {filename}")
        filepath = os.path.join(self.storage_dir, filename)
        if os.path.exists(filepath):
            if filepath not in self.files_open:
                self.files_open[filepath] = 0
            if self.files_open[filepath] != -1:
                send_cmd = "OK"
                client_socket.send(send_cmd.encode(self.format))  # Give Client the OK
                while True:
                    received = client_socket.recv(self.buffer).decode(self.format)
                    if received == "OK":
                        break
                    else:
                        return
                self.files_open[filepath] += 1
                send_file = open(filepath, "rb")
                data = send_file.read(self.buffer)
                while data:  # Sends data a number of bytes equal to the buffer until there is none
                    client_socket.send(data)
                    data = send_file.read(self.buffer)
                self.files_open[filepath] -= 1
                send_file.close()
            else:
                send_cmd = "File Is Being Written"
                client_socket.send(send_cmd.encode(self.format))  # File is currently being written to
        else:
            print("Requested File Not on Server")

    def recv_from_client(self, client_socket, filename):  # Receives a file from the client
        print(f"Receiving File {filename}")
        if os.path.join(self.storage_dir, filename) not in self.files_open:
            self.files_open[os.path.join(self.storage_dir, filename)] = 0
        while self.files_open[os.path.join(self.storage_dir, filename)] > 0:
            continue
        if os.path.exists(os.path.join(self.storage_dir, filename)):
            send_cmd = "FILE_EXISTS"
            client_socket.send(send_cmd.encode(self.format))
            while True:
                received = client_socket.recv(self.buffer).decode(self.format)
                print(received)
                if received == "OK":
                    break
                else:
                    return
        else:
            send_cmd = "OK"
            client_socket.send(send_cmd.encode(self.format))  # Give Client the OK
        self.files_open[os.path.join(self.storage_dir, filename)] = -1
        recv_file = open(os.path.join(self.storage_dir, filename), "wb")
        data = client_socket.recv(self.buffer)
        while data:  # Writes data a number of bytes equal to the buffer until there is none
            recv_file.write(data)
            data = client_socket.recv(self.buffer)
        self.files_open[os.path.join(self.storage_dir, filename)] = 0
        recv_file.close()

    def show_dir(self, client_socket, subfolder):
        print("Showing Directory")
        if os.path.isdir(os.path.join(self.storage_dir, subfolder)):
            send_cmd = "OK"
            client_socket.send(send_cmd.encode(self.format))  # Give Client the OK
            files = os.listdir(str(os.path.join(self.storage_dir, subfolder)))
            while True:
                # Wait for client to give the OK
                received = client_socket.recv(self.buffer).decode(self.format)
                if received == "OK":
                    break
                else:
                    print(received)
                    return
            for file in files:
                if os.path.isdir(os.path.join(self.storage_dir, file)):
                    file = "DIR:"+file
                else:
                    file = "FILE:"+file
                file += "\n"
                client_socket.send(file.encode(self.format))
        else:
            send_cmd = "Invalid Subfolder"
            client_socket.send(send_cmd.encode(self.format))

    def delete_file(self, client_socket, filepath):
        print(f"Deleting File {filepath}")
        if os.path.exists(os.path.join(self.storage_dir, filepath)):
            send_cmd = "OK"
            client_socket.send(send_cmd.encode(self.format))  # Give Client the OK
            if os.path.isdir(os.path.join(self.storage_dir, filepath)):
                self.recursive_delete(filepath)
            else:
                os.remove(os.path.join(self.storage_dir, filepath))
        else:
            send_cmd = "Invalid File to Delete"
            client_socket.send(send_cmd.encode(self.format))  # Give Client the OK

    def recursive_delete(self, filepath):
        print(f"Recursively Deleting {filepath}")
        for file in os.listdir(str(os.path.join(self.storage_dir, filepath))):
            if os.path.isdir(os.path.join(self.storage_dir, file)):
                self.recursive_delete(file)
            else:
                os.remove(os.path.join(self.storage_dir, file))
        os.rmdir(os.path.join(self.storage_dir, filepath))

    def create_subfolder(self, client_socket, subfolder):
        print(f"Creating Subfolder {subfolder}")
        if not os.path.exists(os.path.join(self.storage_dir, subfolder)):
            send_cmd = "OK"
            client_socket.send(send_cmd.encode(self.format))  # Give Client the OK
            os.mkdir(os.path.join(self.storage_dir, subfolder))
        else:
            send_cmd = "SUBFOLDER_EXISTS"
            client_socket.send(send_cmd.encode(self.format))

    def close_server(self):
        self.server.shutdown(1)

    def check_user(self, client_socket, data):
        username, password = data.split(' ', 1)
        result = self.auth.check_password(username, password)
        if result == 0:  # login_successful
            client_socket.send("OK".encode(self.format))
        elif result == 1:  # passwords wrong
            client_socket.send("BAD_PASSWORD".encode(self.format))
        else:  # user not found
            client_socket.send("BAD_USER".encode(self.format))

    def add_user(self, client_socket, data):
        username, password = data.split(' ', 1)
        if self.auth.check_password(username, password) == 2:
            allow = input(f"Allow user {username} to be created? (y/n)\n")
            if allow == "y":
                client_socket.send("OK".encode(self.format))
            else:
                client_socket.send("REFUSED".encode(self.format))
                return
        else:
            client_socket.send("USER_EXISTS".encode(self.format))
            return
        self.auth.add_user(username, password)


folder = ""
while True:
    folder = input("Enter a server folder path:\n")
    if not os.path.exists(folder):
        print("Invalid Path, Try Again")
    elif not os.path.isdir(folder):
        print("Not a Directory, Try Again")
    else:
        break
fo = FileOperator(folder)
atexit.register(fo.close_server)
