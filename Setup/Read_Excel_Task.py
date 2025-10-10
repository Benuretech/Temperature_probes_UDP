"""
Excel data processing utility that converts configuration Excel files to JSON format for the BlueSoft system.
Handles importing test limits, serial number lists, test settings, and default configurations from Excel
spreadsheets and transforms them into structured JSON databases for runtime use.
"""

# ---------------------------------------------------------------------------
import os
import sys
from Setup.Rooth_Path_Finder import rooth_path_finder


PACKAGES_DIR = os.path.join(rooth_path_finder(), "packages")
if PACKAGES_DIR not in sys.path:
    sys.path.insert(0, PACKAGES_DIR)

import json
import pandas as pd
import os.path



class Read_Excel_Task:
    def __init__(self, excel_table):
        self.excel_table = excel_table
        self.SN_tooltype_list = ["212", "275", "275++(2PSU)", "275++(3PSU)"]

        self.limit_dict = {"satus": False}
        self.SN_dict = {"satus": False}
        self.test_setting_dict = {"satus": False}
        self.default_config_dict = {"satus": False}

        self.excel_table.update({"satus": False})
        self.excel_table.update({"SN_tooltype_list": self.SN_tooltype_list})

        self.import_load_limits()
        self.import_SN_list()
        self.import_test_setting()
        self.import_default_config()
        self.excel_dict()

    def import_load_limits(self):

        try:
            root_path = rooth_path_finder()
            limit_raw_table = pd.read_excel(os.path.join(root_path, "Setup/Limits.xlsx"), header=None)
        except Exception as e:
            print(e)
            self.limit_dict["status"] = False
            return False

        limit_raw_table.loc[0:3] = limit_raw_table.loc[0:3].ffill(axis=1)
        limit_raw_table.loc[:, 0:3] = limit_raw_table.loc[:, 0:3].ffill(axis=0)

        lastcolumn = limit_raw_table.shape[1] - 1
        lastrow = limit_raw_table.shape[0]

        for row in range(2, lastrow):  # firstrow-1,lastrow+1
            for col in range(3, lastcolumn):  # firstcolum,lastcolum+1

                level1 = limit_raw_table.loc[0, col]
                level2 = limit_raw_table.loc[row, 0]
                level3 = limit_raw_table.loc[row, 1]
                level4 = limit_raw_table.loc[row, 2]
                level5 = limit_raw_table.loc[1, col]
                value = limit_raw_table.loc[row, col]
                unit = limit_raw_table.loc[row, lastcolumn]

                self.limit_dict.setdefault(level1, {})
                self.limit_dict[level1].setdefault(level2, {})
                self.limit_dict[level1][level2].setdefault(level3, {})
                self.limit_dict[level1][level2][level3].setdefault(level4, {})
                self.limit_dict[level1][level2][level3][level4].setdefault("unit", unit)
                self.limit_dict[level1][level2][level3][level4].setdefault(level5, value)
        root_path = rooth_path_finder()

        self.limit_dict["status"] = True
        return True

    def import_SN_list(self):

        for sheet in self.SN_tooltype_list:  # firstrow,lastrow+1

            try:
                root_path = rooth_path_finder()
                SN_raw_table = pd.read_excel(os.path.join(root_path, "Datafiles/SN_list.xlsx"), header=None, sheet_name=sheet)
            except Exception as e:
                print(e)
                self.SN_dict["status"] = False
                return False

            SN_raw_table.loc[0:3] = SN_raw_table.loc[0:3].ffill(axis=1)

            lastcolumn = SN_raw_table.shape[1]
            for col in range(0, lastcolumn):
                level1 = SN_raw_table.loc[0, col]
                level2 = SN_raw_table.loc[1, col]
                level3 = SN_raw_table.loc[2, col]

                if level3 == "SN":
                    self.SN_dict.setdefault(level1, {})
                    self.SN_dict[level1].setdefault(level2, {})
                    nb_of_sn = SN_raw_table.loc[:, col].last_valid_index() - 2
                    self.SN_dict[level1][level2].setdefault("nbofitem", nb_of_sn)
                    self.SN_dict[level1][level2].setdefault("sn_col", col)
                else:

                    self.SN_dict[level1][level2].setdefault("val_col", {level3: col})

        for sheet in self.SN_tooltype_list:
            root_path = rooth_path_finder()  # firstrow,lastrow+1
            SN_raw_table = pd.read_excel(os.path.join(root_path, "Datafiles/SN_list.xlsx"), header=None, sheet_name=sheet)
            SN_raw_table.loc[0:3] = SN_raw_table.loc[0:3].ffill(axis=1)
            level2_list = self.SN_dict[sheet].keys()
            for level2 in level2_list:
                self.SN_dict[sheet][level2].setdefault("SN_list", {})
                for row_nb in range(3, self.SN_dict[sheet][level2]["nbofitem"] + 3):
                    serialnb = SN_raw_table.loc[row_nb, self.SN_dict[sheet][level2]["sn_col"]]
                    self.SN_dict[sheet][level2]["SN_list"].setdefault(serialnb, {})
                    level3_list = self.SN_dict[level1][level2]["val_col"].keys()
                    for level3 in level3_list:
                        value = SN_raw_table.loc[row_nb, self.SN_dict[sheet][level2]["val_col"][level3]]
                        self.SN_dict[sheet][level2]["SN_list"][serialnb].setdefault(level3, value)
        root_path = rooth_path_finder()
        with open(os.path.join(root_path, "Datafiles/SN.json"), "w") as outfile:
            json.dump(self.SN_dict, outfile)
        self.SN_dict["status"] = True
        return True

    def import_test_setting(self):

        try:
            root_path = rooth_path_finder()
            limit_raw_table = pd.read_excel(os.path.join(root_path, "Datafiles/Test_setting.xlsx"), header=None)
        except Exception as e:
            print(e)
            self.test_setting_dict["status"] = False
            return False

        limit_raw_table = limit_raw_table.astype("object")
        limit_raw_table.loc[0:0] = limit_raw_table.loc[0:0].ffill(axis=1)
        limit_raw_table.loc[:, 0:1] = limit_raw_table.loc[:, 0:1].ffill(axis=0)

        lastcolumn = limit_raw_table.shape[1] - 1
        lastrow = limit_raw_table.shape[0]

        for row in range(1, lastrow):  # firstrow-1,lastrow+1
            for col in range(3, lastcolumn):  # firstcolum,lastcolum+1

                level1 = self.tool_type_conv(limit_raw_table.loc[0, col])
                level2 = limit_raw_table.loc[row, 0]
                level3 = limit_raw_table.loc[row, 1]
                level4 = limit_raw_table.loc[row, 2]
                value = limit_raw_table.loc[row, col]
                if level2 == "PSU" or level2 == "CUP" or level2 == "PWX":
                    value = self.convert_if_no_rounding(value)
                self.test_setting_dict.setdefault(level1, {})
                self.test_setting_dict[level1].setdefault(level2, {})

                if not level3 == "skip":
                    self.test_setting_dict[level1][level2].setdefault(level3, {})
                    self.test_setting_dict[level1][level2][level3].setdefault(level4, value)

                else:
                    self.test_setting_dict.setdefault(level1, {})
                    self.test_setting_dict[level1].setdefault(level2, {})
                    self.test_setting_dict[level1][level2].setdefault(level4, value)

        root_path = rooth_path_finder()
        with open(os.path.join(root_path, "Datafiles/Test_setting.json"), "w") as outfile:
            json.dump(self.test_setting_dict, outfile)
        self.test_setting_dict["status"] = True
        return True

    def tool_type_conv(self, tool_type):
        if isinstance(tool_type, str):
            # Convert to string without `.0` if it's an integer-like float
            value = tool_type
        else:
            # Handle other types (e.g., integers, None, etc.) if necessary
            value = str(int(tool_type))
        return value

    def convert_if_no_rounding(self, value):
        """
        Convert 'value' to int if it's a perfect integer (e.g., '10.0');
        otherwise keep it as float if it's a valid float (e.g., '10.1').
        If it can't be converted to float, leave it unchanged.
        """
        try:
            float_val = float(value)
            # Check if float_val is an integer value (e.g., 10.0, -3.0)
            if float_val.is_integer():
                return int(float_val)  # Convert to int
            else:
                return float_val  # Keep as float
        except ValueError:
            # If float(value) fails (e.g., "abc"), just return original
            return value

    def import_default_config(self):

        try:
            root_path = rooth_path_finder()
            limit_raw_table = pd.read_excel(os.path.join(root_path, "Datafiles/Default_config.xlsx"), header=None)
        except Exception as e:
            print(e)

            self.default_config_dict["status"] = False

            return False

        lastrow = limit_raw_table.shape[0]

        for row in range(0, lastrow):  # firstrow-1,lastrow+1
            level1 = limit_raw_table.loc[row, 0]
            value = limit_raw_table.loc[row, 1]
            self.default_config_dict.setdefault(level1, {})
            self.default_config_dict[level1] = value

        root_path = rooth_path_finder()
        with open(os.path.join(root_path, "Datafiles/default_config.json"), "w") as outfile:
            json.dump(self.default_config_dict, outfile)

        self.default_config_dict["status"] = True
        return True

    def excel_dict(self):

        self.excel_table.update({"limit_dict": self.limit_dict})
        self.excel_table.update({"SN_dict": self.SN_dict})
        self.excel_table.update({"test_setting_dict": self.test_setting_dict})
        self.excel_table.update({"default_config_dict": self.default_config_dict})

        if self.limit_dict["status"] and self.SN_dict["status"] and self.test_setting_dict["status"] and self.default_config_dict["status"]:
            self.excel_table["status"] = True
            return True
        else:
            self.excel_table["status"] = False
            return False
