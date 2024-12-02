import os
import tkinter as tk
from tkinter import filedialog, messagebox
from functools import partial
from authentication import Authentication
from file_requester import FileRequester
from analysis import PerformanceAnalysis
auth = Authentication()
analysis = PerformanceAnalysis()


# very basic UI for the project
# change as any of you see fit, there are placeholders where the buttons don't actually do anything
# there is some error handling, I will continue to expand on it

# Create main window
root = tk.Tk()
root.title("File Management")
root.geometry("500x400")

file_database = {}


# Dictionary to hold users and their passwords (for now, it's a placeholder)
user_database = {}

# Placeholder for the current logged-in user
current_user = None


def show_login_screen():
    clear_window()

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

    password_label = tk.Label(login_frame, text="Do Not share password")
    password_label.pack(pady=5)

    def handle_login():
        username = username_entry.get()
        password = password_entry.get()

        # filling in place holder
        result = file_requester.login(username, password)
        if result == "OK":  # login_successful
            global current_user
            current_user = username
            show_upload_screen()
        elif result == "BAD_PASSWORD":  # passwords wrong
            messagebox.showerror("error", "incorrect password")
        else:  # user not found
            messagebox.showerror("error", "user not found")

    def show_create_user_screen():
        clear_window()

        create_user_frame = tk.Frame(root)
        create_user_frame.pack(pady=10)

        create_username_label = tk.Label(create_user_frame, text="Create Username:")
        create_username_label.pack(pady=5)
        create_username_entry = tk.Entry(create_user_frame)
        create_username_entry.pack(pady=5)

        create_password_label = tk.Label(create_user_frame, text="Create Password:")
        create_password_label.pack(pady=5)
        create_password_entry = tk.Entry(create_user_frame, show="*")
        create_password_entry.pack(pady=5)

        def handle_create_user():
            new_username = create_username_entry.get()
            new_password = create_password_entry.get()

            # replacement code to check if username already exist's
            if new_username and new_password:
                existing_user_status = auth.check_password(new_username, new_password)
                if existing_user_status == 2:
                    auth.add_user(new_username, new_password)
                    messagebox.showinfo("User Created")
                    show_login_screen() 
                else:
                    messagebox.showerror("please fill in both boxes")
            else:
                messagebox.showerror("please fill both boxes")

        create_user_button = tk.Button(create_user_frame, text="Create User", command=handle_create_user)
        create_user_button.pack(pady=10)

        cancel_button = tk.Button(create_user_frame, text="Cancel", command=show_login_screen)
        cancel_button.pack(pady=5)

    # Button to create a new user
    create_user_button = tk.Button(login_frame, text="Create New User", command=show_create_user_screen)
    create_user_button.pack(pady=10)

    # Login button
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

    # replacement code segment
    def handle_ip_submission():
        ip_address = ip_entry.get()
        if ip_address:
            global file_requester
            file_requester = FileRequester(ip_server=ip_address, dest_dir=os.getcwd())
            show_login_screen()
        else:
            messagebox.showerror("Error", "IP Address Invalid")

    ip_button = tk.Button(ip_frame, text="Submit IP", command=handle_ip_submission)
    ip_button.pack(side=tk.LEFT, padx=10)


# handles file upload management screen
def show_upload_screen():
    # file database screen
    clear_window()

    global current_subfolder
    current_subfolder = ""
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

    # replacement for download segment
    def download_file(file_name):
        file_requester.recv_from_server(file_name)

    # replacement for deleting file segment
    def delete_file(file_name):
        file_requester.delete_on_server(file_name)
        if file_name in file_database:
            del file_database[file_name]
        update_file_list()

    # Performance method after file operations
    def upload_file():
        file_path = filedialog.askopenfilename()
        if file_path:
            file_requester.send_to_server(file_path)
            analysis.create_log_file([...])  # to log all data
            update_file_list()

    def select_subfolder(file_name):
        global current_subfolder
        if current_subfolder != "":
            current_subfolder += os.path.sep
        current_subfolder += file_name
        update_file_list()

    def move_dir_up():
        global current_subfolder
        dir_list = current_subfolder.split(os.path.sep)
        dir_list.pop()
        current_subfolder = os.path.sep.join(dir_list)
        update_file_list()

    def update_file_list():
        for widget in file_list_frame.winfo_children():
            widget.destroy()
        dir_display_text = "Current Dir: "
        if current_subfolder == "":
            dir_display_text += "Root"
        else:
            dir_display_text += os.path.sep+current_subfolder
        dir_display.config(text=dir_display_text)
        row = 0
        dir_string = file_requester.show_dir(current_subfolder)
        files = dir_string.split('\n')
        files.pop()

        global file_database
        file_database = {}
        for file in files:
            is_dir, file = file.split(':')
            file_database[file] = is_dir
        for file_name in file_database:
            # Place the file name, download, and delete buttons in a single row
            file_label = tk.Label(file_list_frame, text=file_name)
            file_label.grid(row=row, column=0, padx=5, pady=2, sticky="w")

            # download button if file
            if file_database[file_name] == "FILE":
                download_button = tk.Button(file_list_frame, text="Download", command=partial(download_file, file_name))
                download_button.grid(row=row, column=1, padx=5, pady=2)

            # show dir button if directory
            if file_database[file_name] == "DIR":
                download_button = tk.Button(file_list_frame, text="Show", command=partial(select_subfolder, file_name))
                download_button.grid(row=row, column=1, padx=5, pady=2)

            # delete button
            delete_button = tk.Button(file_list_frame, text="Delete", command=partial(delete_file, file_name))
            delete_button.grid(row=row, column=2, padx=5, pady=2)

            row += 1  # Move to the next row for the next file

        update_scroll_region()

    # Upload button
    upload_button = tk.Button(button_frame, text="Upload File", command=upload_file)
    upload_button.pack(side=tk.LEFT, padx=10)
    move_dir = tk.Button(button_frame, text="Move Directory Up", command=move_dir_up)
    move_dir.pack(side=tk.LEFT, padx=10)
    dir_display = tk.Label(button_frame, text="Current Dir: " + current_subfolder)
    dir_display.pack(side=tk.LEFT, padx=10)
    update_file_list()


def clear_window():
    for widget in root.winfo_children():
        widget.destroy()


show_ip_screen()
root.mainloop()
