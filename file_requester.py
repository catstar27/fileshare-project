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

    def __init__(self, ip_server):
        self.ip_server = ip_server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((self.ip_server, self.port))

    def send_to_server(self, filename):
        if os.path.exists(filename):
            send_cmd = f"recv_from_client {os.path.basename(filename)}"
            self.server.send(send_cmd.encode(self.format))
            while True:
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

    def recv_from_server(self, filename):
        send_cmd = f"send_to_client {filename}"
        self.server.send(send_cmd.encode(self.format))
        while True:
            if self.server.recv(self.buffer).decode(self.format) == "OK":
                break
        recv_file = open(filename, "wb")
        data = self.server.recv(self.buffer)
        while data:
            recv_file.write(data)
            data = self.server.recv(self.buffer)
        self.server.close()
        recv_file.close()

