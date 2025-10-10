"""
Dialog box for creating a new OPCheck test.
"""

import datetime
import os
from Setup.CMD_TABLE import CmdTable
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFileDialog
from PyQt6 import QtWidgets
from GUI.Main_Project.New_Project.New_Project_UI import Ui_New_Project_Dialog
from Setup.Rooth_Path_Finder import rooth_path_finder


class New_Project(QtWidgets.QDialog):

    def __init__(self, Project_para):

        super().__init__()

        self.Ui_New_Project_Dialog_obj = Ui_New_Project_Dialog()  # Create an instance of the UI class
        self.Ui_New_Project_Dialog_obj.setupUi(self)  # Set up the UI


        self.Project_para = Project_para
        self.Project_para.clear()

        self.date_int = int(datetime.datetime.now().timestamp())
        self.full_date_string_dict = self.timestamp_to_string(self.date_int)

        self.Ui_New_Project_Dialog_obj.Date_var.setText(str(self.full_date_string_dict["Day_str"]))
        self.Ui_New_Project_Dialog_obj.Time_var.setText(str(self.full_date_string_dict["Time_str"]))

        # Set the default values
        self.root_path = "C:/Temp_Log"
        self.Ui_New_Project_Dialog_obj.root_path_var.setText(self.root_path)

        self.initial_setting()

    ################################    Check if completed and in view mode    ###########################
    def initial_setting(self):
        self.Ui_New_Project_Dialog_obj.Accept_bt.setEnabled(True)
        self.Ui_New_Project_Dialog_obj.Browse_bt.setEnabled(True)




    ################################    Buttton HMI    ###########################

    def Browser_cmd(self):
        self.dialog = QFileDialog(self)
        if os.path.exists(self.root_path):
            self.dialog.setDirectory(self.root_path)
        self.dialog.setFileMode(QFileDialog.FileMode.Directory)
        dir_name = QFileDialog.getExistingDirectory(self, "Select a Directory")
        if dir_name:
            self.root_path = dir_name
            self.Ui_New_Project_Dialog_obj.root_path_var.setText(self.root_path)

        self.filename_build()

    def Accept_cmd(self):
        self.Apply_cmd()

    def Apply_cmd(self):
        self.filename_build()
        self.Project_para["Project_name"] = self.project_name
        self.Project_para["Project_foldername"] = self.project_foldername
        self.Project_para["Project_path"] = self.project_path
        self.Project_para["Project_filename"] = self.project_filename
        self.Project_para["Root_path"] = self.root_path
        self.Project_para["Date_int"] = self.date_int
        self.Project_para["Date_str"] = self.full_date_string_dict["Date_str"]
        self.Project_para["Time_str"] = self.full_date_string_dict["Time_str"]
        self.Project_para["Day_str"] = self.full_date_string_dict["Day_str"]
        self.done(True)

    def Project_Name_updated(self):
        self.filename_build()
        if self.error_check():
            self.Ui_New_Project_Dialog_obj.Accept_bt.setEnabled(True)            
        else:
            self.Ui_New_Project_Dialog_obj.Accept_bt.setEnabled(False)


    def Cancel_cmd(self):
        self.done(False)

    def filename_build(self):
        self.project_name=self.Ui_New_Project_Dialog_obj.Project_Name_var.text()
        self.project_foldername=self.full_date_string_dict["Date_str"] + "-" + self.project_name        
        self.project_filename=self.project_foldername + ".db"
        self.project_path=self.root_path + "/" + self.project_foldername

        self.Ui_New_Project_Dialog_obj.Date_var.setText(str(self.full_date_string_dict["Day_str"]))
        self.Ui_New_Project_Dialog_obj.Time_var.setText(str(self.full_date_string_dict["Time_str"]))

        self.Ui_New_Project_Dialog_obj.Project_FileName_var.setText(self.project_filename)
        self.Ui_New_Project_Dialog_obj.Project_Path_var.setText(self.project_path)




    def error_check(self):      

        if self.project_path == "":  
            return False  
        
        if self.project_foldername == "":  
            return False 
         
        if self.project_filename == "":  
            return False  


        if os.path.isdir(self.project_path):
            return False

        full_path = os.path.join(self.project_path, self.project_filename)
        if os.path.exists(full_path):
            return False

        return True          

    def timestamp_to_string(self, timestamp):
        """
        Convert a Unix timestamp (int64) to a formatted string.

        Args:
        timestamp (int): Unix timestamp, the number of seconds since 1970-01-01 00:00:00 UTC.

        Returns:
        str: Formatted datetime string in the format "YYYY-MM-DD HH_MM_SS".
        """
        # Convert the timestamp to a datetime object
        date = datetime.datetime.fromtimestamp(timestamp)

        # Format the datetime object into a string with the desired format
        date_string_dict={}
        date_string_dict["Date_str"] = date.strftime("%Y-%m-%d %H_%M_%S")
        date_string_dict["Day_str"] = date.strftime("%Y-%m-%d")
        date_string_dict["Time_str"] = date.strftime("%H_%M_%S")

        return date_string_dict



    def float_test(self, text):
        if text == "":
            return ""

        return float(text)

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


