import os
import socket


class FileRequester:
    """
    This class handles requests to the file operator on the server side.
    This is client side only.
    """
    ip_server = ""
    port = 4450
    buffer = 1024
    format = "utf-8"
    server = None
    dest_dir = ""

    def __init__(self, ip_server, dest_dir):
        self.ip_server = ip_server
        self.dest_dir = dest_dir

    def connect_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((self.ip_server, self.port))

    def send_to_server(self, filename):  # Sends the file at the given path to the server
        self.connect_server()
        if os.path.exists(filename):
            send_cmd = f"recv_from_client {os.path.basename(filename)}"
            self.server.send(send_cmd.encode(self.format))
            while True:
                # Wait for server to give the OK
                received = self.server.recv(self.buffer).decode(self.format)
                if received == "OK":
                    break
                elif received == "FILE_EXISTS":
                    confirm = input("File exists, continue? (y/n)\n")
                    if confirm == 'y':
                        new_send = "OK"
                        self.server.send(new_send.encode(self.format))
                        break
                    else:
                        new_send = "CANCEL"
                        self.server.send(new_send.encode(self.format))
                        break
                else:
                    print(received)
                    return
            send_file = open(filename, "rb")
            data = send_file.read(self.buffer)
            while data:
                self.server.send(data)
                data = send_file.read(self.buffer)
            send_file.close()
        else:
            print("Requested File Not on Server")
        self.server.close()

    def recv_from_server(self, filename):  # Receives a file with the given name from the server
        self.connect_server()
        send_cmd = f"send_to_client {filename}"
        self.server.send(send_cmd.encode(self.format))
        while True:
            # Wait for server to give the OK
            received = self.server.recv(self.buffer).decode(self.format)
            if received == "OK":
                break
            else:
                print(received)
                return
        try:
            recv_file = open(os.path.join(self.dest_dir, filename), "wb")
        except PermissionError or FileNotFoundError:
            print("Error Writing File")
        else:
            data = self.server.recv(self.buffer)
            while data:
                recv_file.write(data)
                data = self.server.recv(self.buffer)
            recv_file.close()
        self.server.close()

    def show_dir(self):
        self.connect_server()
        send_cmd = "show_dir"
        self.server.send(send_cmd.encode(self.format))
        while True:
            # Wait for server to give the OK
            received = self.server.recv(self.buffer).decode(self.format)
            if received == "OK":
                break
            else:
                print(received)
                return
        try:
            data = self.server.recv(self.buffer).decode(self.format)
            while data:
                print(data, end='')
                data = self.server.recv(self.buffer).decode(self.format)
        except UnicodeDecodeError:
            print("Error Displaying Directory")
        self.server.close()

    def delete_on_server(self, filepath):
        self.connect_server()
        send_cmd = f"delete_server_file {filepath}"
        self.server.send(send_cmd.encode(self.format))
        while True:
            # Wait for server to give the OK
            received = self.server.recv(self.buffer).decode(self.format)
            if received == "OK":
                break
            else:
                print(received)
                return
        self.server.close()

    def create_subfolder(self, filepath):
        self.connect_server()
        send_cmd = f"create_subfolder {filepath}"
        self.server.send(send_cmd.encode(self.format))
        while True:
            # Wait for server to give the OK
            received = self.server.recv(self.buffer).decode(self.format)
            if received == "OK":
                break
            else:
                print(received)
                return
        self.server.close()

