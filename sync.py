import os
import shutil
import threading
import tkinter as tk
from tkinter import ttk






class SyncFiles:
    def __init__(self, root, src_folder, dst_folder, progress_bar, status):
        self.root = root
        self.src_folder = src_folder
        self.dst_folder = dst_folder
        self.progress_bar = progress_bar
        self.status = status
        

    def sync(self):
        # Create a set of all files in the source folder
        src_files = set()
        for root, dirs, files in os.walk(self.src_folder):
            for file in files:
                src_files.add(os.path.relpath(os.path.join(root, file), self.src_folder))

        # Create a set of all files in the destination folder
        dst_files = set()
        for root, dirs, files in os.walk(self.dst_folder):
            for file in files:
                dst_files.add(os.path.relpath(os.path.join(root, file), self.dst_folder))

        # Delete any files in the destination folder that don't exist in the source folder
        for file in dst_files - src_files:
            dst_file = os.path.join(self.dst_folder, file)
            os.remove(dst_file)
            self.status.set(f"Deleted {os.path.relpath(dst_file, self.dst_folder)}")

        # Synchronize the remaining files
        for root, dirs, files in os.walk(self.src_folder):
            # Get the destination folder path by replacing the source folder path with the destination folder path
            dst_root = root.replace(self.src_folder, self.dst_folder, 1)

            # Make sure the destination directory exists, if not, create it
            if not os.path.isdir(dst_root):
                os.makedirs(dst_root)

            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dst_root, file)

                # Check if the file already exists in the destination folder and if it's older than the source file
                if not os.path.isfile(dst_file) or os.stat(src_file).st_mtime - os.stat(dst_file).st_mtime > 1:
                    # Copy the file to the destination folder
                    shutil.copy2(src_file, dst_file)

                    # Update the progress bar and status label
                    self.progress_bar.step(1)
                    self.status.set(f"Synchronized {os.path.relpath(src_file, self.src_folder)}")
                    self.root.update()

class SyncThread(threading.Thread):
    def __init__(self, sync):
        threading.Thread.__init__(self)
        self.sync = sync

    def run(self):
        self.sync.sync()
        self.sync.status.set("Sync completed")
        self.sync.root.after(2000, self.sync.root.destroy)

# Read the source and destination folder paths from the config file
with open("config.txt") as f:
    config = f.read().splitlines()
    src_folder = config[0]
    dst_folder = config[1]

# Create the GUI
root = tk.Tk()
root.title("Sync Files")
#center window
width = 300 # Width 
height = 90 # Height

screen_width = root.winfo_screenwidth()  # Width of the screen
screen_height = root.winfo_screenheight() # Height of the screen
 
# Calculate Starting X and Y coordinates for Window
x = (screen_width/2) - (width/2)
y = (screen_height/2) - (height/2)
 
root.geometry(

'%dx%d+%d+%d' % (width, height, x, y))

# Create the status label
status = tk.StringVar()
status_label = ttk.Label(root, textvariable=status)

# Create the progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")

# Create the layout
progress_bar.pack(pady=10)
status_label.pack(pady=5)

# Start the synchronization process in a separate thread
sync = SyncFiles(root, src_folder, dst_folder, progress_bar, status)
sync_thread = SyncThread(sync)
sync_thread.start()

root.mainloop()
