import os
import socket
import time
from analysis import PerformanceAnalysis as pa
from tkinter import messagebox

analysis = pa()


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
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((self.ip_server, self.port))
        except ConnectionRefusedError:
            messagebox.askyesno("Connection Error",
                                f"Could not connect to ip {self.ip_server}. Is the server running?")

    def send_to_server(self, filename):  # Sends the file at the given path to the server
        self.connect_server()
        if os.path.exists(filename):
            send_cmd = f"recv_from_client {os.path.basename(filename)}"
            self.server.send(send_cmd.encode(self.format))
            response_start_time = time.time() # Measure time
            
            while True:
                # Wait for server to give the OK
                received = self.server.recv(self.buffer).decode(self.format)
                if received == "OK":
                    response_time = time.time() - response_start_time
                    break
                elif received == "FILE_EXISTS":
                    confirm = messagebox.askyesno("File Exists",
                                                  f"File {filename} exists on server, do you wish to overwrite")
                    if confirm:
                        new_send = "OK"
                        self.server.send(new_send.encode(self.format))
                        response_time= time.time() - response_start_time
                        break
                    else:
                        new_send = "CANCEL"
                        self.server.send(new_send.encode(self.format))
                        break
                else:
                    print(received)
                    return
            send_file = open(filename, "rb")

            # Variables for performance analysis
            total_size = os.path.getsize(filename)
            data_sent = 0
            transfer_log = []
            transfer_start_time = time.time()
            last_append_time = time.time()
            filename = os.path.basename(filename)
            data = send_file.read(self.buffer)
            while data:                
                self.server.send(data)
                data_sent += len(data)
                
                # Performance analysis
                current_time = time.time()
                elapsed_time = current_time - response_start_time
                if elapsed_time > 0:
                    data_rate = data_sent / elapsed_time
                data = send_file.read(self.buffer)
                
                if current_time - last_append_time >= 0.1: 
                    transfer_log.append([
                        elapsed_time,
                        data_rate / 1048576
                    ])        
                    last_append_time = current_time
            transfer_end_time = time.time()
            send_file.close()
            
            transfer_time = transfer_end_time - transfer_start_time
            transfer_rate = total_size / transfer_time if transfer_time > 0 else 0
            
            store_data = [
                    filename,
                    "Upload",
                    f"{total_size / 1048576:.2f}",
                    f"{response_time:.2f}",
                    f"{transfer_time:.2f}",
                    f"{transfer_rate / 1e6:.2f}"
                ]
            analysis.create_log_file(store_data)     
            analysis.plot_data_rate_graph(filename, transfer_log, "Upload")
        else:
            print("Requested File Not on Server")
        self.server.close()

    def recv_from_server(self, filename):  # Receives a file with the given name from the server
        self.connect_server()
        send_cmd = f"send_to_client {filename}"
        self.server.send(send_cmd.encode(self.format))
        response_start_time = time.time()
        while True:
            # Wait for server to give the OK
            received = self.server.recv(self.buffer).decode(self.format)
            if received == "OK":
                response_time = time.time() - response_start_time
                break
            else:
                print(received)
                return
        try:
            recv_file = open(os.path.join(self.dest_dir, filename), "wb")
        except PermissionError or FileNotFoundError:
            print("Error Writing File")
        else:
            # Variables for performance analysis
            filename = os.path.basename(filename)
            total_size = os.path.getsize(os.path.join(self.dest_dir, filename))
            data_received = 0
            transfer_log = []
            transfer_start_time = time.time()
            last_append_time = time.time()
            self.server.send("OK".encode(self.format))
            data = self.server.recv(self.buffer)
            while data:
                recv_file.write(data)
                data = self.server.recv(self.buffer)
                data_received += len(data)
                # Performance analysis
                current_time = time.time()
                elapsed_time = current_time - response_start_time
                if elapsed_time > 0:
                    data_rate = data_received / elapsed_time
                
                if current_time - last_append_time >= 0.1: 
                    transfer_log.append([
                        elapsed_time,
                        data_rate / 1048576
                    ])        
                    last_append_time = current_time
            transfer_end_time = time.time()
            
            transfer_time = transfer_end_time - transfer_start_time
            transfer_rate = total_size / transfer_time if transfer_time > 0 else 0
            store_data = [
                    filename,
                    "Download",
                    f"{total_size / 1048576:.2f}",
                    f"{response_time:.2f}",
                    f"{transfer_time:.2f}",
                    f"{transfer_rate / 1e6:.2f}"
                ]
            analysis.create_log_file(store_data)     
            analysis.plot_data_rate_graph(filename, transfer_log, "Download")
            
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
        server_dir = ""
        try:
            self.server.send("OK".encode(self.format))
            data = self.server.recv(self.buffer).decode(self.format)
            while data:
                server_dir += data
                data = self.server.recv(self.buffer).decode(self.format)
        except:
            print("Error Displaying Directory")
        self.server.close()
        return server_dir

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

    def login(self, username, password):
        self.connect_server()
        send_cmd = f"login {username} {password}"
        self.server.send(send_cmd.encode(self.format))
        while True:
            # Wait for server to give the OK
            received = self.server.recv(self.buffer).decode(self.format)
            if received:
                break
        self.server.close()
        return received
