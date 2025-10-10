
import os
import sys
from Setup.Rooth_Path_Finder import rooth_path_finder
# Add the packages directory to the system path FIRST
# This allows importing modules from the packages directory without modifying PYTHONPATH
PACKAGES_DIR = os.path.join(rooth_path_finder(), "packages")
if PACKAGES_DIR not in sys.path:
    sys.path.insert(0, PACKAGES_DIR)

# Now import GUI modules that depend on PyQt6
from GUI.Main_Project.Main_Project import Main_Project
import multiprocessing as mp
import logging
import time
import atexit
import psutil
import traceback
import msvcrt

from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QGuiApplication

# Custom Imports

from Driver.RJ45_UDP import RJ45_UDP
from Setup.Queue_Setup import Queue_Group_Creator






# Function to handle application exit
def on_exit():
    # Signal all processes to exit
    exit_process.set()
    print("Application exiting, signaling processes to exit.")




# Function to check if a process with a given PID is running
def is_process_running(pid):
    try:
        p = psutil.Process(pid)
        return p.is_running()
    except psutil.NoSuchProcess:
        return False


# Function to create a lock file to prevent multiple script instances
def create_lock_file():
    root_path = rooth_path_finder()
    lock_file = os.path.join(root_path, "scriptlock.pid")

    print("check lock file")
    print(lock_file)

    if os.path.exists(lock_file):
        print("lock file exists")
        with open(lock_file, "r") as f:
            try:
                old_pid = int(f.read().strip())
            except ValueError:
                old_pid = None

        if old_pid and is_process_running(old_pid):
            print(f"Script is already running (PID={old_pid}). Exiting.")
            sys.exit(1)
        else:
            print(f"Script was terminated (PID={old_pid}). Replacing.")
            os.remove(lock_file)
            with open(lock_file, "w") as f:
                f.write(str(os.getpid()))
            atexit.register(remove_lock_file)
    else:
        print("No lock file found. Creating new one.")
        with open(lock_file, "w") as f:
            f.write(str(os.getpid()))
        atexit.register(remove_lock_file)


# Function to remove the lock file on exit
def remove_lock_file():
    root_path = rooth_path_finder()
    lock_file = os.path.join(root_path, "scriptlock.pid")
    if os.path.exists(lock_file):
        os.remove(lock_file)




def RJ45_UDP_thread(q_group, exit_process):
    print("DEBUG: RJ45_UDP_thread started")
    RJ45_UDP_p = psutil.Process(os.getpid())
    try: RJ45_UDP_p.cpu_affinity([4, 5])
    except Exception: pass
    try: RJ45_UDP_p.nice(psutil.HIGH_PRIORITY_CLASS)
    except Exception: pass

    print("DEBUG: About to create RJ45_UDP object")

    try: 
        RJ45_UDP_obj = RJ45_UDP(q_group)
        print("DEBUG: RJ45_UDP object created successfully")
    except Exception as e: 
        print(f"DEBUG: Failed to create RJ45_UDP object: {e}")
        print("DEBUG: RJ45_UDP_thread exiting due to creation failure")
        return

    print("DEBUG: Starting main loop")
    try:
        while not exit_process.is_set():
            RJ45_UDP_obj.read_ppp()

    except Exception as e:
        print(f"DEBUG: Exception in main loop: {e}")
    finally:
        print("RJ45_UDP_thread: clean exit")
        sys.exit(0)

def QT_thread(q_group, exit_process):
    print("DEBUG: QT_thread started")
    qt_p = psutil.Process(os.getpid())
    qt_p.cpu_affinity([2, 3])
    qt_p.nice(psutil.HIGH_PRIORITY_CLASS)

    print("DEBUG: Creating Qt application")
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(
        """
    QPushButton {
        background-color: #f0f0f0;
    }
    QTextEdit {
        background-color: #dddeea;
    }
    QTableWidget {
        background-color: #dddeea;
        border: 1px solid #999;
    }
    QTableWidget::item {
        padding: 0px;    /* remove space inside cell */
        margin: 0px;
    }
    """
    )
    print("DEBUG: Creating Main_Project window")
    main_window = Main_Project(q_group)
    print("DEBUG: Showing main window")
    main_window.showMaximized()
    print("DEBUG: Main window shown successfully")

    # Local exit handler
    def handle_exit():
        exit_process.set()
        app.quit()

    # Timer for checking exit condition
    timer = QTimer()
    timer.timeout.connect(lambda: handle_exit() if exit_process.is_set() else None)
    timer.start(100)

    # Connect window close to exit process
    main_window.destroyed.connect(handle_exit)

    # Global exception handler for the Qt thread. Any unhandled exceptions inside the Qt thread will be caught here and will make the process exit.
    def qt_exception_handler(exctype, value, tb):
        print("Unhandled exception in Qt thread:")
        traceback.print_exception(exctype, value, tb)
        exit_process.set()  # Notify main process
        sys.exit(1)  # Exit this process

    sys.excepthook = qt_exception_handler

    print("DEBUG: Starting Qt event loop")
    sys.exit(app.exec())



if __name__ == "__main__":
    if sys.platform == "win32":
        mp.set_start_method("spawn", force=True)

    create_lock_file()
    main_p = psutil.Process(os.getpid())
    main_p.cpu_affinity([0, 1])
    main_p.nice(psutil.HIGH_PRIORITY_CLASS)

    exit_process = mp.Event()
    procs = []


    try:
        QT_q_group_obj = Queue_Group_Creator({"RJ45_UDP": 20,})
        QT_q_group = QT_q_group_obj.q_group_dict  # Get the queue group dictionnary


        # Start processes
        procs.append(mp.Process(target=RJ45_UDP_thread, args=(QT_q_group, exit_process)))
        procs.append(mp.Process(target=QT_thread, args=(QT_q_group, exit_process)))

        print("DEBUG: Starting processes...")
        process_names = ["RJ45_UDP_thread", "QT_thread"]
        for i, p in enumerate(procs):
            print(f"DEBUG: Starting process {process_names[i]}")
            p.start()
            print(f"DEBUG: Process {process_names[i]} started with PID {p.pid}")

        print("Press any key to stop… (or Ctrl+C)")
        try:
            process_check_counter = 0
            while all(p.is_alive() for p in procs):
                process_check_counter += 1

                
                if msvcrt.kbhit():
                    msvcrt.getch()
                    print("Key pressed. Shutting down…")
                    break
                time.sleep(0.2)
            
            # If we exit the loop, check which process(es) died
            for i, p in enumerate(procs):
                if not p.is_alive():
                    print(f"DEBUG: Process {process_names[i]} (PID {p.pid}) has died with exit code: {p.exitcode}")
        except KeyboardInterrupt:
            print("Ctrl+C. Shutting down…")

        # 3) Signal children and wait
        exit_process.set()
        for p in procs: p.join(timeout=2)
        for p in procs:
            if p.is_alive():
                p.terminate(); p.join()


            

    except Exception as e:
        print(f"Error: {e}")
        exit_process.set()
    finally:
        # Final cleanup
        for p in procs:
            if p.is_alive():
                p.terminate()
        remove_lock_file()
