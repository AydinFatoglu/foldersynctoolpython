import tkinter as tk
import shutil
import os
import configparser

class FolderSync:
    def __init__(self, src_folder, dest_folder):
        self.src_folder = src_folder
        self.dest_folder = dest_folder
        self.total_files = 0
        self.synced_files = 0
        self.synced_size = 0

    def sync(self):
        # clear the destination folder if the source folder is empty
        if not os.listdir(self.src_folder):
            shutil.rmtree(self.dest_folder)
            os.makedirs(self.dest_folder)
            self.progress_var.set("Sync complete!")
            self.progress.update()
            return

        # create a set of all files in the source folder
        src_files = set()
        for root, dirs, files in os.walk(self.src_folder):
            for file in files:
                src_files.add(os.path.join(root, file))

        # delete files from the destination folder that are not in the source folder
        for root, dirs, files in os.walk(self.dest_folder):
            for file in files:
                dest_file_path = os.path.join(root, file)
                if dest_file_path not in src_files:
                    os.remove(dest_file_path)

        # copy files from the source folder to the destination folder
        for root, dirs, files in os.walk(self.src_folder):
            for file in files:
                src_file_path = os.path.join(root, file)
                dest_file_path = os.path.join(self.dest_folder, os.path.relpath(src_file_path, self.src_folder))
                dest_folder_path = os.path.dirname(dest_file_path)

                if not os.path.exists(dest_folder_path):
                    os.makedirs(dest_folder_path)

                if not os.path.exists(dest_file_path) or (os.path.exists(dest_file_path) and (os.stat(src_file_path).st_mtime - os.stat(dest_file_path).st_mtime > 1)):
                    shutil.copy2(src_file_path, dest_file_path)
                    self.synced_files += 1
                    self.synced_size += os.stat(src_file_path).st_size
                self.total_files += 1

                self.progress_var.set(f"Synced {self.synced_files}/{self.total_files} files ({self.synced_size / (1024 * 1024):.2f} MB)")
                self.progress.update()

        self.progress_var.set("Sync complete!")
        self.progress.update()

    def start_sync(self):
        self.window = tk.Tk()
        self.window.title("Folder Sync Tool")
        
        #center window
        width = 300 # Width 
        height = 90 # Height

        screen_width = self.window.winfo_screenwidth()  # Width of the screen
        screen_height = self.window.winfo_screenheight() # Height of the screen
 
        # Calculate Starting X and Y coordinates for Window
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
 
        self.window.geometry(

        '%dx%d+%d+%d' % (width, height, x, y))

        self.progress_var = tk.StringVar()
        self.progress_var.set("Syncing files...")
        self.progress = tk.Label(self.window, textvariable=self.progress_var)
        self.progress.pack(pady=10)

        self.sync()

        self.window.mainloop()

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")

    src_folder = config.get("folders", "source_folder")
    dest_folder = config.get("folders", "destination_folder")

    folder_sync = FolderSync(src_folder, dest_folder)
    folder_sync.start_sync()
