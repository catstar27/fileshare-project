import tkinter as tk
from tkinter import filedialog, messagebox
from functools import partial

#very basic UI for the project
#change as any of you see fit, there are placeholders where the buttons don't actually do anything
#there is some error handling, I will continue to expand on it

# Create main window
root = tk.Tk()
root.title("File Management")
root.geometry("500x400")

file_database = {}


# Handles login loop
def show_login_screen():
    # Clear the window and show login spot
    clear_window()

    # Frame for login
    login_frame = tk.Frame(root)
    login_frame.pack(pady=10)

    username_label = tk.Label(login_frame, text="Username:")
    username_label.pack(pady=5)
    username_entry = tk.Entry(login_frame)
    username_entry.pack(pady=5)

    password_label = tk.Label(login_frame, text="Password:")
    password_label.pack(pady=5)
    password_entry = tk.Entry(login_frame, show="*")
    password_entry.pack(pady=5)

    def handle_login():
        username = username_entry.get()
        password = password_entry.get()

        #Placeholder, add actual authentication
        if username and password:  # Checks if username and password were entered
            show_ip_screen()  # Proceed to IP input after successful login
        else:
            messagebox.showerror("Error", "Please enter both username and password.")

    login_button = tk.Button(login_frame, text="Login", command=handle_login)
    login_button.pack(pady=10)


# handles IP address input screen
def show_ip_screen():
    # show IP input screen
    clear_window()

    ip_frame = tk.Frame(root)
    ip_frame.pack(pady=10)
    ip_label = tk.Label(ip_frame, text="Enter IP Address:")
    ip_label.pack(side=tk.LEFT)


    ip_entry = tk.Entry(ip_frame, width=25)
    ip_entry.pack(side=tk.LEFT)


    def handle_ip_submission(): #does the ip submission
        ip_address = ip_entry.get()
        if ip_address:
            #placeholder add actual ip address connection
            show_upload_screen()  # Proceed to file upload screen if anything ip is entered
        else:
            messagebox.showerror("Error", "Please enter a valid IP address.")

    ip_button = tk.Button(ip_frame, text="Submit IP", command=handle_ip_submission)
    ip_button.pack(side=tk.LEFT, padx=10)


#handles file upload management screen
def show_upload_screen():
    # file database screen
    clear_window()

    # Frame for uploaded files and scrollable canvas
    file_frame = tk.Frame(root)
    file_frame.pack(pady=15, fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(file_frame)
    scrollbar = tk.Scrollbar(file_frame, orient="vertical", command=canvas.yview)
    canvas.config(yscrollcommand=scrollbar.set)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    file_list_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=file_list_frame, anchor="nw")

    # Function to update the scroll region
    def update_scroll_region():
        file_list_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    # Button Frame
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    def upload_file():
        file_path = filedialog.askopenfilename()
        if file_path:
            # Check if the file exists in the dictionary
            file_name = file_path.split("/")[-1]
            if file_name in file_database:
                # Ask user if they want to replace the file
                replace = messagebox.askyesno("File Exists",
                                              f"File '{file_name}' already exists. Do you want to replace it?")
                if replace:
                    file_database[file_name] = file_path
                    # Update the UI
                    update_file_list()
            else:
                # Simulate adding file to the database
                file_database[file_name] = file_path
                update_file_list()

    def download_file(file_name):
        # just show a message box for now
        messagebox.showinfo("Download", f"Downloading file: {file_name}")

    def delete_file(file_name):
        if file_name in file_database:
            del file_database[file_name]
            messagebox.showinfo("Deleted", f"File '{file_name}' has been deleted.")
            update_file_list()

    def update_file_list():
        for widget in file_list_frame.winfo_children():
            widget.destroy()

        row = 0
        for file_name in file_database:
            # Place the file name, download, and delete buttons in a single row
            file_label = tk.Label(file_list_frame, text=file_name)
            file_label.grid(row=row, column=0, padx=5, pady=2, sticky="w")

            # download button
            download_button = tk.Button(file_list_frame, text="Download", command=partial(download_file, file_name))
            download_button.grid(row=row, column=1, padx=5, pady=2)

            # upload button
            delete_button = tk.Button(file_list_frame, text="Delete", command=partial(delete_file, file_name))
            delete_button.grid(row=row, column=2, padx=5, pady=2)

            row += 1  # Move to the next row for the next file

        update_scroll_region()

    # Upload button
    upload_button = tk.Button(button_frame, text="Upload File", command=upload_file)
    upload_button.pack(side=tk.LEFT, padx=10)


    update_file_list()


def clear_window():
    for widget in root.winfo_children():
        widget.destroy()



show_login_screen()


root.mainloop()
