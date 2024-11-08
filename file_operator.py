import os
import shutil


class FileOperator:
    """
    This class handles file operations by storing a working directory.
    To be used on the server side only, not on client.
    """
    storage_dir = ""
    def __init__(self, _storage_dir):
        if os.path.isdir(os.path.abspath(_storage_dir)):
            self.storage_dir = os.path.abspath(_storage_dir)
            print(self.storage_dir)
        else:
            print("Invalid Directory")

    def import_file(self, file):
        if os.path.exists(os.path.abspath(file)):
            shutil.copy(os.path.abspath(file), self.storage_dir)
        else:
            print("Could Not Find File to Import")

    def export_file(self, filename, destination):
        if os.path.exists(os.path.join(self.storage_dir, filename)) and os.path.isdir(os.path.abspath(destination)):
            shutil.copy(str(os.path.join(self.storage_dir, filename)), os.path.abspath(destination))
        elif not os.path.exists(self.storage_dir+filename):
            print("Invalid Export File")
        else:
            print("Invalid Directory to Transfer")
