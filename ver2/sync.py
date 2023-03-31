import os
import shutil
import threading
import configparser
import tkinter as tk
import subprocess

config = configparser.ConfigParser()
config.read("config.ini")

source_dir = config.get("Folders", "Source")
dest_dir = config.get("Folders", "Destination")
exe_path = config.get("Executable", "Path")

class SyncApp:
    def __init__(self, root):
        self.root = root
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to sync.")
        self.status_label = tk.Label(root, textvariable=self.status_var)
        self.status_label.pack(pady=10)
        threading.Thread(target=self.sync_files).start()

    def sync_files(self):
        try:
            for root, dirs, files in os.walk(source_dir):
                # copy directories first
                for dir in dirs:
                    source_dir_path = os.path.join(root, dir)
                    dest_dir_path = os.path.join(dest_dir, os.path.relpath(source_dir_path, source_dir))
                    os.makedirs(dest_dir_path, exist_ok=True)

                # copy files
                for file in files:
                    source_file_path = os.path.join(root, file)
                    dest_file_path = os.path.join(dest_dir, os.path.relpath(source_file_path, source_dir))
                    os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
                    shutil.copy2(source_file_path, dest_file_path)
                    self.status_var.set(f"Syncing {os.path.relpath(source_file_path, source_dir)}...")
                    self.root.update()

            self.status_var.set("Files synced successfully.")
            subprocess.Popen(exe_path)
            self.root.destroy()  # Close the app after running the executable.

        except Exception as e:
            self.status_var.set(f"An error occurred: {str(e)}")
            self.root.after(1000, lambda: self.root.destroy())  # Wait 5 seconds before closing the app.


if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Sync App")
    app = SyncApp(root)
    root.mainloop()
