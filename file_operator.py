import os
import socket
import threading


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

    def __init__(self, _storage_dir):
        if os.path.isdir(os.path.abspath(_storage_dir)):
            self.storage_dir = os.path.abspath(_storage_dir)
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.ip_server, self.port))
            self.server_listen()
        else:
            print("Invalid Directory")

    def server_listen(self):
        self.server.listen()
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=[conn, addr])
            thread.start()

    def handle_client(self, conn, addr):
        print(f"Handling Connection at {addr}")
        connected = True
        while connected:
            cmd = conn.recv(self.buffer).decode(self.format)
            cmd = cmd.split(' ', 1)
            if cmd[0] == "send_to_client":
                self.send_to_client(conn, cmd[1])
                break
            elif cmd[0] == "recv_from_client":
                self.recv_from_client(conn, cmd[1])
                break
            else:
                print(f"Invalid Request: {cmd[0]}")

    def send_to_client(self, client_socket, filename):  # Sends a file to the client
        if os.path.exists(os.path.join(self.storage_dir, filename)):
            send_cmd = "OK"
            client_socket.send(send_cmd.encode(self.format))  # Give Client the OK
            send_file = open(os.path.join(self.storage_dir, filename), "rb")
            data = send_file.read(self.buffer)
            while data:  # Sends data a number of bytes equal to the buffer until there is none
                client_socket.send(data)
                data = send_file.read(self.buffer)
            client_socket.shutdown(2)
            client_socket.close()
            send_file.close()
        else:
            print("Requested File Not on Server")

    def recv_from_client(self, client_socket, filename):  # Receives a file from the client
        print(f"Receiving File {filename}")
        send_cmd = "OK"
        client_socket.send(send_cmd.encode(self.format))  # Give Client the OK
        recv_file = open(os.path.join(self.storage_dir, filename), "wb")
        data = client_socket.recv(self.buffer)
        while data:  # Writes data a number of bytes equal to the buffer until there is none
            recv_file.write(data)
            data = client_socket.recv(self.buffer)
        client_socket.close()
        recv_file.close()

