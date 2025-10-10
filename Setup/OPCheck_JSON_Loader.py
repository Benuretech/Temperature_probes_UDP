"""
JSON configuration loader for the OPCheck system that assembles database structures from multiple sources.
Handles loading of test limits, serial number lists, and general configuration files with automatic
version detection and fallback mechanisms for robust configuration management.
"""

# Standard library imports
import os
import json
import re
from datetime import datetime

# Custom import for finding the root path
from Setup.Rooth_Path_Finder import rooth_path_finder


# Loader class for OPCheck JSON configuration and database files
class OPCheck_JSON_Loader:
    def __init__(self):
        # Placeholder for database, not used as instance variable
        database = {}

    def Load(self, custom_file_path=None):
        """
        Loads the main OPCheck database and configuration files, including SN lists and test limits.
        If a specific config file is provided, it attempts to load it; otherwise, loads the latest config.
        Returns the assembled database dictionary.
        """
        # Find the root path for the project
        root_path = rooth_path_finder()
        data_base = {}

        # Load the main OPCheck database JSON
        Database_file_path = os.path.join(root_path, "Setup/OPCheck_database.json")
        with open(Database_file_path, "r") as json_file:
            data_base = json.load(json_file)

        # Initialize ConfigBase section
        data_base.update({"ConfigBase": {}})

        # Add supported SN tool types
        data_base["ConfigBase"].update({"SN_tooltype_list": ["212", "275", "275++(2PSU)", "275++(3PSU)"]})

        # Load the latest SN list JSON file
        path = os.path.join(root_path, "Config/SN")
        SN_List_file_path = self.find_latest_file_by_timestamp(path, ending_str="SN_list.json")
        SN_filename = os.path.splitext(os.path.basename(SN_List_file_path))[0]

        with open(SN_List_file_path, "r") as json_file:
            data_base["ConfigBase"].update({"SN_dict": json.load(json_file)})

        config_loaded_flag = False
        # Try to load a custom config file if provided
        if custom_file_path:
            try:
                path = os.path.join(root_path, "Config/OPCheck_Config")
                OPCheck_Config_file_path = os.path.join(path, custom_file_path)
                with open(OPCheck_Config_file_path, "r") as json_file:
                    jsonfile = json.load(json_file)
                    data_base["ConfigBase"].update({"limit_dict": jsonfile["Test_Limits_dict"], "default_config_dict": jsonfile["General_Config_dict"], "test_setting_dict": jsonfile["test_setting_dict"]})
                Config_filename = os.path.splitext(os.path.basename(OPCheck_Config_file_path))[0]
                config_loaded_flag = True
            except:
                # If loading custom config fails, fallback to latest config
                config_loaded_flag = False

        # If no custom config or failed to load, use the latest config file
        if config_loaded_flag == False:
            path = os.path.join(root_path, "Config/OPCheck_Config")
            OPCheck_Config_file_path = self.find_latest_file_by_timestamp(path, ending_str="OPCheck_Config.json")
            with open(OPCheck_Config_file_path, "r") as json_file:
                jsonfile = json.load(json_file)
                data_base["ConfigBase"].update({"limit_dict": jsonfile["Test_Limits_dict"], "default_config_dict": jsonfile["General_Config_dict"], "test_setting_dict": jsonfile["test_setting_dict"]})
            Config_filename = os.path.splitext(os.path.basename(OPCheck_Config_file_path))[0]

        data_base["ConfigBase"]["SN_dict"].update({"SN_File_Rev": SN_filename})
        data_base["ConfigBase"].update({"Config_File_Rev": Config_filename})
        data_base["Test"]["SN"].update({"Config_File_Rev": Config_filename})
        data_base["Test"]["SN"].update({"SN_File_Rev": SN_filename})

        return data_base

    def find_latest_file_by_timestamp(self, directory, ending_str=".json"):
        """
        Finds the latest file in a directory matching a date and index pattern in the filename.
        Example filename: YYYY_MM_DD_XX_<ending_str>
        Returns the full path to the latest file, or None if not found.
        """
        latest_file = None
        latest_date = None
        latest_index = -1

        # Regex pattern: captures YYYY_MM_DD and XX from the filename prefix
        pattern = re.compile(r"^(\d{4}_\d{2}_\d{2})_(\d{2})_" + re.escape(ending_str) + r"$")

        for filename in os.listdir(directory):
            match = pattern.match(filename)
            if match:
                date_part, index_part = match.groups()
                try:
                    file_date = datetime.strptime(date_part, "%Y_%m_%d")
                    file_index = int(index_part)
                except ValueError:
                    continue  # Skip any invalid formats

                # Choose newer file by date, then index
                if latest_date is None or file_date > latest_date or (file_date == latest_date and file_index > latest_index):
                    latest_date = file_date
                    latest_index = file_index
                    latest_file = os.path.join(directory, filename)

        return latest_file  # None if no match
