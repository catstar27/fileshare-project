import os
import socket


class FileRequester:
    """
    This class handles requests to the file operator on the server side.
    This is client side only.
    An instance of this class exists to perform one operation only.
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
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((self.ip_server, self.port))

    def send_to_server(self, filename):  # Sends the file at the given path to the server
        if os.path.exists(filename):
            send_cmd = f"recv_from_client {os.path.basename(filename)}"
            self.server.send(send_cmd.encode(self.format))
            while True:
                # Wait for server to give the OK
                if self.server.recv(self.buffer).decode(self.format) == "OK":
                    break
            send_file = open(filename, "rb")
            data = send_file.read(self.buffer)
            while data:
                self.server.send(data)
                data = send_file.read(self.buffer)
            self.server.close()
            send_file.close()
        else:
            print("Requested File Not on Server")

    def recv_from_server(self, filename):  # Receives a file with the given name from the server
        send_cmd = f"send_to_client {filename}"
        self.server.send(send_cmd.encode(self.format))
        while True:
            # Wait for server to give the OK
            if self.server.recv(self.buffer).decode(self.format) == "OK":
                break
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
        finally:
            self.server.close()

