from plyer import filechooser
import os

path_to_return = "connected folder: none"

def on_file_selected(path):
    global path_to_return
    try:
        path_to_return = str(path[0])
    except Exception:
        pass
def open():
    start_path = os.path.expanduser("~")
    filechooser.choose_dir(on_selection=on_file_selected, path = start_path)

