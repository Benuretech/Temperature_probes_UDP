"""
This script converts all .ui files in the current folder and its subfolders to .py files using PyQt6's pyuic module.
It starts from the current folder and traverses all subfolders to find .ui files. The converted .py files are saved in the same folders as the original .ui files.
"""

import os
import subprocess
import sys
from Setup.Rooth_Path_Finder import rooth_path_finder
PACKAGES_DIR = os.path.join(rooth_path_finder(), "packages")
if PACKAGES_DIR not in sys.path:
    sys.path.insert(0, PACKAGES_DIR)

def convert_pyqt_ui(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".ui"):
                ui_file_path = os.path.join(root, file)
                py_file_name = file.replace(".ui", ".py")
                py_file_path = os.path.join(root, py_file_name)

                # Ensure the subprocess uses the local packages directory for PyQt6
                env = os.environ.copy()
                env["PYTHONPATH"] = PACKAGES_DIR + os.pathsep + env.get("PYTHONPATH", "")

                try:
                    subprocess.run(
                        [
                            sys.executable, "-m", "PyQt6.uic.pyuic",
                            ui_file_path,
                            "-o",
                            py_file_path,
                        ],
                        check=True,
                        env=env
                    )  # replace with your pyuic6 path
                    print(f"Successfully converted {ui_file_path} to {py_file_path}")
                except subprocess.CalledProcessError as e:
                    print(f"Error converting {ui_file_path}: {e}")


# Main function to execute the conversion
if __name__ == "__main__":
    current_folder = os.path.dirname(
        os.path.abspath(__file__)
    )  # Get the current folder's absolute path
    convert_pyqt_ui(
        current_folder
    )  # convert all .ui files in the current folder and its subfolders