import matplotlib.pyplot as plt
import os
import csv
from datetime import datetime

# Paths
filename = "metrics_log.csv"
logs_folder = "logs"
current_dir = os.getcwd()
save_path = os.path.join(current_dir, logs_folder)
metrics_log_datapath = os.path.join(current_dir, logs_folder, filename)

class PerformanceAnalysis():
    def __init__(self):
        pass
    
    def plot_data_rate_graph(self, filename, data_rate, type):
        elapsed_time = [entry[0] for entry in data_rate]
        transfer_rate = [entry[1] for entry in data_rate]
        
        plt.figure(figsize=(10, 6))
        plt.plot(elapsed_time, transfer_rate, marker="o", linestyle="-", color="b", label="Data Rate")
        plt.title(f"{type} Rate Over Time for {filename}", fontsize=14)
        plt.xlabel("Elapsed Time (s)", fontsize=12)
        plt.ylabel("Data Rate (MB/s)", fontsize=12)
        plt.grid(True)
        plt.legend()
        
        add_filename = f"data_rate_{filename}.png"

        full_save_path = os.path.join(save_path, add_filename)
        plt.savefig(full_save_path)
        plt.show()
        
    def create_log_file(self, stored_data):
        metrics_log_exists = os.path.isfile(metrics_log_datapath)
        
        # Get current date and time to differentiate between files with same name
        current_datetime = datetime.now()
        
        stored_data.append(current_datetime)
        
        with open(metrics_log_datapath, "a", newline='') as log_file:
            csv_writer = csv.writer(log_file)
            
            # Creates files if it does not exist
            if not metrics_log_exists:
                csv_writer.writerow(["Filename", "Type (Download or Upload)", "File Size (MB)", "Response Time (s)", "Transfer Time (s)", "Transfer Rate (MB/s)", "Date"])
            csv_writer.writerow(stored_data)