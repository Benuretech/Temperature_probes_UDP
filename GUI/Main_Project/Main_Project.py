"""
Main GUI window for performing BlueSoft operations.
Provides comprehensive GUI for creating, editing, and managing operations.
Handles database interactions, real-time updates, and operation workflow management.
"""
import pickle
from pathlib import Path
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtGui import QDoubleValidator, QValidator
from PyQt6.QtWidgets import QAbstractItemView, QProgressDialog, QFileDialog, QMessageBox
from PyQt6.QtGui import QColor, QBrush, QFont

from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtWidgets import QStyledItemDelegate, QStyle
import shutil, tempfile
from GUI.Main_Project.Main_Project_UI import Ui_Main_Project
from dvg_ringbuffer import RingBuffer


from GUI.Main_Project.New_Project.New_Project import New_Project
from GUI.Main_Project.Graphics.Temp_Graph import Temp_Graph
from Setup.Operation_JSON_Loader import Operation_JSON_Loader
import csv
from Setup.Rooth_Path_Finder import rooth_path_finder

from Setup.Queue_Setup import Main_Queue_port

from Setup.DataBaseWrap import (
    DataBaseWrap,
    Project,
    Sample,
)
from sqlalchemy.orm import joinedload
import re
import numpy as np
from sqlalchemy import func
import time
import json
import os
import tempfile
import copy




def brighten_color(color: QColor, brightness_factor=1.6, saturation_factor=1.1):
    """Returns a brighter and slightly more saturated version of the color."""
    h, s, v, a = color.getHsvF()
    v = min(1.0, v * brightness_factor)
    s = min(1.0, s * saturation_factor)
    return QColor.fromHsvF(h, s, v, a)

class BrightSelectionDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        color = index.data(Qt.ItemDataRole.BackgroundRole)

        if isinstance(color, QBrush):
            color = color.color()

        if option.state & QStyle.StateFlag.State_Selected:
            # Brighten the original color
            if isinstance(color, QColor):
                highlight_color = brighten_color(color)
                painter.fillRect(option.rect, highlight_color)
            else:
                painter.fillRect(option.rect, option.palette.highlight())

            # Set bold font
            font = option.font
            font.setBold(True)
            painter.setFont(font)

        elif isinstance(color, QColor):
            painter.fillRect(option.rect, color)

        super().paint(painter, option, index)


class CustomDoubleValidator(QDoubleValidator):
    """
    A custom QDoubleValidator that invalidates input containing commas.

    This validator extends the standard QDoubleValidator to specifically
    reject any input strings that uses a comma (','), typically used as a decimal
    separator in some locales, ensuring that only periods ('.') are accepted as
    decimal separators.
    """

    def validate(self, input_str: str, pos: int) -> tuple:
        """
        Validates the input string.

        If the input string contains a comma (','), the input is considered
        invalid. Otherwise, the validation is delegated to the parent
        QDoubleValidator's validate method.

        Args:
            input_str: The string to validate.
            pos: The current cursor position in the input string.

        Returns:
            A tuple (QValidator.State, str, int) indicating the validation
            state, the input string, and the cursor position.
            Returns (QValidator.State.Invalid, input_str, pos) if a comma is found.
        """
        if "," in input_str:
            return (QValidator.State.Invalid, input_str, pos)
        return super().validate(input_str, pos)


class Main_Project(QtWidgets.QMainWindow):

    def __init__(self, q_group):
        """
        Initializes the Temp_Graph window.

        This constructor sets up the main window for the operation,
        initializes UI elements, establishes communication queues,
        loads necessary data, and configures initial states for
        various operational parameters and checks.

        Args:
            q_group (any): An object representing a group of queues,
                           used for inter-process communication.
        """
        super().__init__()  # Initialize the QMainWindow
        self.Ui_Main_Project_obj = Ui_Main_Project()  # Create an instance of the UI class
        self.Ui_Main_Project_obj.setupUi(self)


        self._init_start(q_group)



        self.show()



    def _init_start(self, q_group):
        """Initializes communication ports and queues."""
        self.q_group = q_group
        self.Main_Port_obj = Main_Queue_port(q_group)
        self.Port = self.Main_Port_obj.Port
        self.project_created = False
        self.DB = DataBaseWrap()
        self.topic_data = {}
        self.Temp_Graph_view = Temp_Graph(self.Ui_Main_Project_obj.Temp_Graph_widget_obj, title="MQTT Topics", x_label="Time", y_label="Value")
        self.refresh_timer()
        self.database_write_timer()
        self.Buffer_Sample_List = []
        self.init_time=0
        self.init_date=0
        self.max_buffer_size = 1000 # Max samples to keep in memory per topic







    def _load_app_data(self):
        """Loads application data from JSON and sets related UI elements."""

        # load the database template of the operation dictionary
        root_path = rooth_path_finder()
        Operation_JSON_Loader_obj = Operation_JSON_Loader()
        self.data_base = copy.deepcopy(Operation_JSON_Loader_obj.Load())

        self.Ui_Main_Project_obj.Operation_BlueSoft_run_Rev_lb.setText(self.BlueSoft_Operation_rev)



    ################################   refresh timer    ###########################
    def refresh_timer(self):
        """Sets up a periodic update mechanism for refreshing the GUI display."""
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.refresh_display)
        self.timer.start()


    ################################   refresh timer    ###########################
    def database_write_timer(self):
        """Sets up a periodic update mechanism for refreshing the GUI display."""
        self.timer2 = QtCore.QTimer()
        self.timer2.setInterval(1000)
        self.timer2.timeout.connect(self.database_write)
        self.timer2.start()



    ################################    Buttton HMI    ###########################

    def Quit_cmd(self):

        self.close()

    def closeEvent(self, event):        
        QCoreApplication.instance().quit()



    def refresh_display(self):
        new_update = False

        while self.Port["RJ45_UDP"].receive_fifo():

            incoming = self.Port["RJ45_UDP"].JSON_in
            new_update = False

            # Case 1: JSON_in is a dict like {"topic": (timestamp, value), ...}
            if isinstance(incoming, dict):
                for topic, data in incoming.items():
                    try:
                        ts, payload = data  # payload already numeric
                    except (TypeError, ValueError):
                        print(f"⚠️ Invalid data format for topic {topic}: {data}")
                        continue
                    if isinstance(payload, (int, float)):
                        if self.init_time == 0:
                            self.init_time = ts
                            self.init_date = time.strftime("%H_%M_%S")

                        self.append_sample(topic, (ts - self.init_time), payload)                        

                        new_update = True
                    else:
                        print(f"⚠️ Non-numeric payload for topic {topic}: {payload}")

            # Case 2: JSON_in is a list of dicts: [{"topic": (timestamp, value)}, ...]
            elif isinstance(incoming, list):
                for item in incoming:
                    if not isinstance(item, dict):
                        continue
                    for topic, data in item.items():
                        try:
                            ts, payload = data
                        except (TypeError, ValueError):
                            print(f"⚠️ Invalid data format for topic {topic}: {data}")
                            continue
                        if isinstance(payload, (int, float)):   
                            if self.init_time == 0:
                                self.init_time = ts
                                self.init_date = time.strftime("%H_%M_%S")

                            self.append_sample(topic, (ts - self.init_time), payload)

                            new_update = True
                        else:
                            print(f"⚠️ Non-numeric payload for topic {topic}: {payload}")

            else:
                print(f"⚠️ Unexpected JSON_in type: {type(incoming)!r}")

        if new_update:
            # Convert ring buffers to numpy arrays for the graph
            topic_arrays = {}
            for topic, ring_buffer in self.topic_data.items():
                topic_arrays[topic] = np.asarray(ring_buffer)
            self.Temp_Graph_view.set_topic_data(topic_arrays)



    def database_write(self):
        if self.project_created == True:
            if self.Buffer_Sample_List:
                with self.DB.get_session() as session:
                    try:
                        # Bulk insert all samples in the buffer
                        samples_to_add = [
                            Sample(
                                project_key=self.DB.project_DB.project_key,
                                topic=topic,
                                time=t_sec,
                                value=payload
                            )
                            for topic, t_sec, payload in self.Buffer_Sample_List
                        ]
                        session.bulk_save_objects(samples_to_add)
                        session.commit()
                        print(f"Inserted {len(samples_to_add)} samples into the database.")
                        self.Buffer_Sample_List.clear()  # Clear the buffer after successful insert
                    except Exception as e:
                        session.rollback()
                        print(f"Error inserting samples into database: {e}")
    



    def append_sample(self, topic: str, ts_ns, payload):
        """
        Append a (time, value) sample for a topic.
        - ts_ns: timestamp in nanoseconds (e.g., time.perf_counter_ns())
        - payload: numeric value (int/float). If bytes arrive by mistake, we try to decode once.
        """

        # Ensure numeric payload (be tolerant to the occasional bytes)
        if isinstance(payload, (bytes, bytearray)):
            try:
                payload = float(payload.decode("ascii"))
            except Exception as e:
                print(f"Invalid (non-numeric) payload for {topic}: {payload!r} ({e})")
                return
        else:
            try:
                payload = float(payload)
            except Exception as e:
                print(f"Invalid payload type for {topic}: {payload!r} ({e})")
                return

        # Convert ns → seconds
        t_sec = float(ts_ns) * 1e-9

        # If topic not yet created, initialize its array
        if topic not in self.topic_data:
            self.topic_data[topic] = RingBuffer(capacity=self.max_buffer_size, dtype=(np.float64, 2))

        # Append row [time_sec, value]
        self.topic_data[topic].append([t_sec, payload])
        self.Buffer_Sample_List.append((topic, t_sec, payload))

    ################################   Button Task CMD ###########################

    def New_Project_cmd(self):
        self.hide()
        self.Project_para = {}
        New_Project_obj = New_Project(self.Project_para)
        result = New_Project_obj.exec()
        self.show()  # Show the GUI
        if result == True:
            # Create the project folder first before connecting to database
            self.create_folder(self.Project_para["Project_path"])
            
            full_path = os.path.join(self.Project_para["Project_path"], self.Project_para["Project_filename"])
            self.DB.connect_DB(full_path)
            self.project_created = True

            self.Ui_Main_Project_obj.Date_var.setText(self.Project_para["Day_str"])
            self.Ui_Main_Project_obj.Time_var.setText(self.Project_para["Time_str"])
            self.Ui_Main_Project_obj.Project_Name_var.setText(self.Project_para["Project_name"])
            self.Ui_Main_Project_obj.FileName_var.setText(self.Project_para["Project_filename"])
            self.Ui_Main_Project_obj.Project_Path_var.setText(self.Project_para["Project_path"])




            with self.DB.get_session() as session:
                new_project=Project()

                new_project.Name = self.Project_para["Project_name"]
                new_project.FolderName = self.Project_para["Project_foldername"]
                new_project.FileName = self.Project_para["Project_filename"]                                
                new_project.Path = self.Project_para["Project_path"]

                new_project.date_int = self.Project_para["Date_int"]
                new_project.date_str = self.Project_para["Date_str"]
                new_project.time_str = self.Project_para["Time_str"]
                new_project.day_str = self.Project_para["Day_str"]
                session.add(new_project)
                session.commit()


    def Save_cvs_cmd(self):
        """
        Export database samples to CSV format.
        - If project DB exists: Use current DB and save CSV in same folder with init_date appended
        - If no project DB: Browse for DB file and save CSV in same folder with init_date appended
        CSV structure: topic[1] time value topic[2] time value ...
        Each topic gets 3 columns: topic_name, time, value
        """
        try:
            temp_db = None
            db_file_path = None
            csv_file_path = None
            
            # Check if we have a current project database
            if self.project_created and self.DB.linked:
                # Use current project database
                db_file_path = self.DB.db_file_path
                temp_db = self.DB  # Use existing connection
                
                # Generate CSV filename in same folder as database
                db_dir = os.path.dirname(db_file_path)
                db_filename_no_ext = os.path.splitext(os.path.basename(db_file_path))[0]
                
                # Append init_date if available, otherwise use current time
                if hasattr(self, 'init_date') and self.init_date != 0:
                    date_suffix = self.init_date
                else:
                    date_suffix = time.strftime("%H_%M_%S")
                
                csv_filename = f"{db_filename_no_ext}_{date_suffix}.csv"
                csv_file_path = os.path.join(db_dir, csv_filename)
                
                print(f"Using current project database: {db_file_path}")
                print(f"CSV will be saved as: {csv_file_path}")
                
            else:
                # No current project, browse for database file
                db_file_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Select Database File",
                    "",
                    "Database files (*.db *.sqlite *.sqlite3);;All files (*.*)"
                )
                
                if not db_file_path:
                    return  # User cancelled
                
                # Generate CSV filename in same folder as selected database
                db_dir = os.path.dirname(db_file_path)
                db_filename_no_ext = os.path.splitext(os.path.basename(db_file_path))[0]
                
                # Use init_date if available, otherwise use current time
                if hasattr(self, 'init_date') and self.init_date != 0:
                    date_suffix = self.init_date
                else:
                    date_suffix = time.strftime("%H_%M_%S")
                
                csv_filename = f"{db_filename_no_ext}_{date_suffix}.csv"
                csv_file_path = os.path.join(db_dir, csv_filename)
                
                # Create a temporary database connection
                temp_db = DataBaseWrap()
                temp_db.connect_DB(db_file_path)
                
                print(f"Using selected database: {db_file_path}")
                print(f"CSV will be saved as: {csv_file_path}")
            
            # Export data to CSV
            with temp_db.get_session() as session:
                # Get all samples ordered by time
                samples = session.query(Sample).order_by(Sample.time).all()
                
                if not samples:
                    QMessageBox.information(
                        self,
                        "No Data",
                        "No samples found in the database."
                    )
                    return
                
                # Group samples by topic
                topics_data = {}
                for sample in samples:
                    topic = sample.topic
                    if topic not in topics_data:
                        topics_data[topic] = []
                    topics_data[topic].append({
                        'time': sample.time,
                        'value': sample.value
                    })
                
                # Sort topics for consistent column ordering
                sorted_topics = sorted(topics_data.keys())
                
                print(f"Found {len(sorted_topics)} topics: {sorted_topics}")
                print(f"Total samples: {len(samples)}")
                
                # Create CSV headers
                headers = []
                for topic in sorted_topics:
                    headers.extend([f"{topic}_topic", f"{topic}_time", f"{topic}_value"])
                
                # Find the maximum number of samples across all topics
                max_samples = max(len(topics_data[topic]) for topic in sorted_topics) if sorted_topics else 0
                
                # Write CSV file
                with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write headers
                    writer.writerow(headers)
                    
                    # Write data rows
                    for row_idx in range(max_samples):
                        row_data = []
                        for topic in sorted_topics:
                            topic_samples = topics_data[topic]
                            if row_idx < len(topic_samples):
                                # Data exists for this topic at this row
                                sample = topic_samples[row_idx]
                                row_data.extend([topic, sample['time'], sample['value']])
                            else:
                                # No more data for this topic, add empty cells
                                row_data.extend(["", "", ""])
                        writer.writerow(row_data)
                
                print(f"CSV exported successfully to: {csv_file_path}")
                print(f"Exported {max_samples} rows with {len(sorted_topics)} topics")
                
                # Show success message to user
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Database exported successfully!\n\n"
                    f"Source: {os.path.basename(db_file_path)}\n"
                    f"CSV File: {os.path.basename(csv_file_path)}\n"
                    f"Location: {db_dir}\n"
                    f"Topics: {len(sorted_topics)}\n"
                    f"Rows: {max_samples}\n"
                    f"Total samples: {len(samples)}"
                )
        
        except Exception as e:
            error_msg = f"Error exporting database to CSV: {str(e)}"
            print(error_msg)
            QMessageBox.critical(
                self,
                "Export Error",
                error_msg
            )
        finally:
            # Clean up temporary database connection (only if we created a new one)
            if temp_db is not None and temp_db != self.DB and hasattr(temp_db, 'linked') and temp_db.linked:
                temp_db.engine.dispose()


    def decode_date32_str(self,val: int) -> str:
        """VAL is a signed 32-bit int from struct '<i'. Return 'YYYY_MM_DD' """
        if val is None:
            return ""
        v = val & 0xFFFFFFFF
        y = (v >> 16) & 0xFFFF
        m = (v >> 8)  & 0xFF
        d =  v        & 0xFF
        return f"{y:04d}{"_"}{m:02d}{"_"}{d:02d}"



    def safe_write(self, file_path, data):
        dir_name, base_name = os.path.split(file_path)
        temp_file = tempfile.NamedTemporaryFile(mode="w", dir=dir_name, delete=False)

        try:
            with temp_file as f:
                f.write(data)

            os.replace(temp_file.name, file_path)
        except Exception as e:
            os.remove(temp_file.name)
            raise e

    def safe_read(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                return file.read()
        return ""

    def float_test(self, text):
        try:
            float_format = float(text)
        except:
            float_format = 0.0

        return float_format

    def int_test(self, text):
        try:
            int_format = int(text)
        except:
            int_format = 0  # Default to 0 if conversion fails
        return int_format

    def ascii_float(self, value, dec_numb):
        try:
            # Construct the format string based on the number of decimals
            format_str = "%." + str(dec_numb) + "f"
            # Format the value
            formatted_value = format_str % float(value)
        except (ValueError, TypeError):
            # If the value cannot be converted to float, handle the error
            formatted_value = ""  # or any appropriate default handling

        return formatted_value

    def extract_float(value):
        # Use a regular expression to match a floating-point number at the start of the string
        match = re.match(r"([-+]?\d*\.\d+|\d+)", value)
        if match:
            return float(match.group())  # Convert matched value to float
        return None  # Return None if no number is found

    def m_f(self, value_m, value_f):
        if self.metric:
            return value_m
        else:
            return value_f

    def create_folder(self, folder):
        try:
            # Create the folder and any necessary parent directories
            os.makedirs(folder, exist_ok=True)
        except OSError as error:
            print(f"Error creating folder {folder}: {error}")
