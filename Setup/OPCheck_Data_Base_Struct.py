"""
Database structure definition for OPCheck system with comprehensive test data initialization.
"""

from Setup.Limit_Check import LimitCheck
import copy


class OPCheck_Data_Base_Struct:
    def __init__(self):

        self.limit_check_obj = LimitCheck()
        self.warning = self.limit_check_obj.warning

        # initialize the data base
        self.data_base = {}
        # initialize the Excel data base
        self.data_base.update({"MCU": {}})
        self.data_base.update({"PICO": {}})
        self.data_base.update({"Live_SBO": {}})

        self.data_base["PICO"].update({"picoscope_model": False})
        self.data_base["PICO"].update({"picoscope_ready": False})  # Picoscope ready flag
        self.data_base["PICO"].update({"Task": "Wait"})  # Task being executed, "PWX_test"/"PSU_test"/ "Wait" for no task
        self.data_base["PICO"].update({"Status": "Stop"})  # Task status, "Run"/"Stop"/"terminate"/"Done"/"Time_Out"/"Shot"
        self.data_base["PICO"].update({"Result": {}})  # Time of the PSU test start

        self.data_base.update({"CMD": {}})
        # initialize the Test data base
        self.data_base.update({"Test": {}})

        # initialize the OPCheck data base

        self.data_base["Test"].update({"Template": {}})
        self.data_base["Test"].update({"Properties": {}})
        self.data_base["Test"]["Properties"].update({"date": None, "Original_date": None, "Original_date_str_1": None, "author": None, "test_name": None, "root_path": None, "Folder": None, "File": None, "Path": None, "selected": None, "Iteration": None, "BlueSoft_OPCheck_Rev": None})

        # initialize the SBO data base
        self.data_base["Test"].update({"SBO": {}})
        self.data_base["Test"]["SBO"].update({"selected": None})
        self.data_base["Test"]["SBO"].update({"Path": None})
        self.data_base["Test"]["SBO"].update({"File": None})
        self.data_base["Test"]["SBO"].update({"Result": {}})

        self.data_base["Test"]["SBO"]["Result"].update({"status": self.warning["NA"]})

        # initialize the SBO test data base
        self.data_base["Test"]["SBO"]["Result"].update({"VERSION": {"val": None, "status": self.warning["NA"]}})


        self.data_base["Test"]["SBO"]["Result"].update({"I_Leackage": {}})
        self.data_base["Test"]["SBO"]["Result"].update({"R100": {}})
        self.data_base["Test"]["SBO"]["Result"].update({"R300": {}})
        self.data_base["Test"]["SBO"]["Result"].update({"V_Tolerance": {}})
        self.data_base["Test"]["SBO"]["Result"].update({"I_Tolerance": {}})

        # initialize the Component SBO data base
        self.data_base["Test"]["SBO"]["Result"].update({"RJ45_ST": {}})
        self.data_base["Test"]["SBO"]["Result"].update({"RS485_ST": {}})
        self.data_base["Test"]["SBO"]["Result"].update({"CAL_ST": {}})
        self.data_base["Test"]["SBO"]["Result"].update({"PICO": {}})
        self.data_base["Test"]["SBO"]["Result"].update({"SSR_ST": {}})

        # initialize the limit SBO calibration data base
        self.data_base["Test"]["SBO"]["Result"]["I_Leackage"].update({"lim": {"unit": "V", "LL": -0.01, "L": -0.0099, "H": 0.0099, "HH": 0.01}})
        self.data_base["Test"]["SBO"]["Result"]["R100"].update({"lim": {"unit": "Ohms", "LL": 95, "L": 96, "H": 104, "HH": 105}})
        self.data_base["Test"]["SBO"]["Result"]["R300"].update({"lim": {"unit": "Ohms", "LL": 295, "L": 296, "H": 304, "HH": 305}})
        self.data_base["Test"]["SBO"]["Result"]["V_Tolerance"].update({"lim": {"unit": "%", "LL": -2, "L": -1.9, "H": 1.9, "HH": 2}})
        self.data_base["Test"]["SBO"]["Result"]["I_Tolerance"].update({"lim": {"unit": "%", "LL": -2, "L": -1.9, "H": 1.9, "HH": 2}})

        # initialize the val SBO calibration data base
        self.data_base["Test"]["SBO"]["Result"]["I_Leackage"].update({"val": None})
        self.data_base["Test"]["SBO"]["Result"]["R100"].update({"val": None})
        self.data_base["Test"]["SBO"]["Result"]["R300"].update({"val": None})
        self.data_base["Test"]["SBO"]["Result"]["V_Tolerance"].update({"val": None})
        self.data_base["Test"]["SBO"]["Result"]["I_Tolerance"].update({"val": None})

        # initialize the status SBO calibration data base
        self.data_base["Test"]["SBO"]["Result"]["I_Leackage"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SBO"]["Result"]["R100"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SBO"]["Result"]["R300"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SBO"]["Result"]["V_Tolerance"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SBO"]["Result"]["I_Tolerance"].update({"status": self.warning["NA"]})

        # initialize the val SBO calibration data base
        self.data_base["Test"]["SBO"]["Result"]["RJ45_ST"].update({"val": None})
        self.data_base["Test"]["SBO"]["Result"]["RS485_ST"].update({"val": None})
        self.data_base["Test"]["SBO"]["Result"]["CAL_ST"].update({"val": None})
        self.data_base["Test"]["SBO"]["Result"]["PICO"].update({"val": None})
        self.data_base["Test"]["SBO"]["Result"]["SSR_ST"].update({"val": None})

        # initialize the SBO data base
        self.data_base["Test"].update({"SN": {}})
        self.data_base["Test"]["SN"].update({"selected": None})
        self.data_base["Test"]["SN"].update({"ToolType": None})
        self.data_base["Test"]["SN"].update({"Config_File_Rev": None})
        self.data_base["Test"]["SN"].update({"SN_File_Rev": None})
        self.data_base["Test"]["SN"].update({"File": None})
        self.data_base["Test"]["SN"].update({"Path": None})

        self.data_base["Test"]["SN"].update({"SBO": {}})
        self.data_base["Test"]["SN"].update({"CUP": {}})
        self.data_base["Test"]["SN"].update({"PSD": {}})
        self.data_base["Test"]["SN"].update({"PSU1": {}})
        self.data_base["Test"]["SN"].update({"PSU2": {}})
        self.data_base["Test"]["SN"].update({"PSU3": {}})
        self.data_base["Test"]["SN"].update({"PWX": {}})
        self.data_base["Test"]["SN"].update({"RED": {}})
        self.data_base["Test"]["SN"].update({"CPB": {}})

        self.data_base["Test"]["SN"]["SBO"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["CUP"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["PSD"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["SN"]["PSU1"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["PSU2"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["PSU3"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["PWX"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["RED"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["CPB"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["SN"]["SBO"].update({"Serial_nb": None})
        self.data_base["Test"]["SN"]["CUP"].update({"Serial_nb": None})
        self.data_base["Test"]["SN"]["PSD"].update({"Serial_nb": None})
        self.data_base["Test"]["SN"]["PSU1"].update({"Serial_nb": None})
        self.data_base["Test"]["SN"]["PSU2"].update({"Serial_nb": None})
        self.data_base["Test"]["SN"]["PSU3"].update({"Serial_nb": None})
        self.data_base["Test"]["SN"]["PWX"].update({"Serial_nb": None})
        self.data_base["Test"]["SN"]["RED"].update({"Serial_nb": None})
        self.data_base["Test"]["SN"]["CPB"].update({"Serial_nb": None})

        self.data_base["Test"]["SN"]["PSU1"].update({"enable": True})
        self.data_base["Test"]["SN"]["PSU2"].update({"enable": False})
        self.data_base["Test"]["SN"]["PSU3"].update({"enable": False})

        self.data_base["Test"]["SN"]["CUP"].update({"Resistance": {}})
        self.data_base["Test"]["SN"]["PSD"].update({"Resistance": {}})
        self.data_base["Test"]["SN"]["PSD"].update({"Continuity": {}})
        self.data_base["Test"]["SN"]["PSU1"].update({"Capacitance": {}})
        self.data_base["Test"]["SN"]["PSU2"].update({"Capacitance": {}})
        self.data_base["Test"]["SN"]["PSU3"].update({"Capacitance": {}})
        self.data_base["Test"]["SN"]["PWX"].update({"Dull_Resistance": {}})
        self.data_base["Test"]["SN"]["PWX"].update({"Pressure": {}})
        self.data_base["Test"]["SN"]["RED"].update({"Coefficient": {}})
        self.data_base["Test"]["SN"]["RED"].update({"Resistance": {}})
        self.data_base["Test"]["SN"]["RED"].update({"Continuity": {}})
        self.data_base["Test"]["SN"]["CPB"].update({"Coefficient": {}})

        self.data_base["Test"]["SN"]["RED"].update({"Coefficient": {}})

        self.data_base["Test"]["SN"]["CUP"]["Resistance"].update({"val": None})
        self.data_base["Test"]["SN"]["PSD"]["Resistance"].update({"val": None})
        self.data_base["Test"]["SN"]["PSD"]["Continuity"].update({"val": None})
        self.data_base["Test"]["SN"]["PSU1"]["Capacitance"].update({"val": None})
        self.data_base["Test"]["SN"]["PSU2"]["Capacitance"].update({"val": None})
        self.data_base["Test"]["SN"]["PSU3"]["Capacitance"].update({"val": None})
        self.data_base["Test"]["SN"]["PWX"]["Dull_Resistance"].update({"val": None})
        self.data_base["Test"]["SN"]["PWX"]["Pressure"].update({"val": None})
        self.data_base["Test"]["SN"]["RED"]["Coefficient"].update({"val": None})
        self.data_base["Test"]["SN"]["RED"]["Continuity"].update({"val": None})
        self.data_base["Test"]["SN"]["RED"]["Resistance"].update({"val": None})
        self.data_base["Test"]["SN"]["CPB"]["Coefficient"].update({"val": None})

        self.data_base["Test"]["SN"]["CUP"]["Resistance"].update({"lim": None})
        self.data_base["Test"]["SN"]["PSD"]["Resistance"].update({"lim": None})
        self.data_base["Test"]["SN"]["PSD"]["Continuity"].update({"lim": None})
        self.data_base["Test"]["SN"]["PSU1"]["Capacitance"].update({"lim": None})
        self.data_base["Test"]["SN"]["PSU2"]["Capacitance"].update({"lim": None})
        self.data_base["Test"]["SN"]["PSU3"]["Capacitance"].update({"lim": None})
        self.data_base["Test"]["SN"]["PWX"]["Dull_Resistance"].update({"lim": None})
        self.data_base["Test"]["SN"]["RED"]["Resistance"].update({"lim": None})
        self.data_base["Test"]["SN"]["RED"]["Continuity"].update({"lim": None})
        self.data_base["Test"]["SN"]["RED"]["Coefficient"].update({"lim": None})
        self.data_base["Test"]["SN"]["CPB"]["Coefficient"].update({"lim": None})

        self.data_base["Test"]["SN"]["CUP"]["Resistance"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["PSD"]["Resistance"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["PSD"]["Continuity"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["PSU1"]["Capacitance"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["PSU2"]["Capacitance"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["PSU3"]["Capacitance"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["PWX"]["Dull_Resistance"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["RED"]["Resistance"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["RED"]["Continuity"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["RED"]["Coefficient"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["SN"]["CPB"]["Coefficient"].update({"status": self.warning["NA"]})

        # initialize the SBO data base
        self.data_base["Test"].update({"CUP": {}})
        self.data_base["Test"]["CUP"].update({"selected": None})
        self.data_base["Test"]["CUP"].update({"Path": None})
        self.data_base["Test"]["CUP"].update({"File": None})
        self.data_base["Test"]["CUP"].update({"Result": {}})

        self.data_base["Test"]["CUP"].update({"Setting": {}})
        self.data_base["Test"]["CUP"].update({"Time": None})

        #  self.data_base["Test"]["CUP"]["Setting"].update({"Start_Voltage":None,"Stop_Voltage":None,"End_Voltage":None,"Current_max":None,"Ramp_up_time":None,"Ramp_Idle":None,"Ramp_down_time":None})

        self.data_base["Test"]["CUP"]["Setting"].update({"Mask": None, "V1": None, "T1_2": None, "V2": None, "T2_3": None, "T3_4": None, "V4": None, "Current_max": None})

        self.data_base["Test"]["CUP"]["Result"].update({"ASD_TS_flag": "Unknown"})
        self.data_base["Test"]["CUP"]["Result"].update({"Analysis_status": None})
        self.data_base["Test"]["CUP"]["Result"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["CUP"]["Result"].update({"BT": {}})

        self.data_base["Test"]["CUP"]["Result"]["BT"].update({"Start": {}})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["Start"].update({"coord": {"p": None, "t": None, "V": None, "I": None}})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["Start"].update({"val": None})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["Start"].update({"lim": None})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["Start"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["CUP"]["Result"]["BT"].update({"I300V": {}})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["I300V"].update({"coord": {"p": None, "t": None, "V": None, "I": None}})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["I300V"].update({"val": None})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["I300V"].update({"lim": None})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["I300V"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["CUP"]["Result"]["BT"].update({"I500V": {}})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["I500V"].update({"coord": {"p": None, "t": None, "V": None, "I": None}})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["I500V"].update({"val": None})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["I500V"].update({"lim": None})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["I500V"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["CUP"]["Result"]["BT"].update({"Stop": {}})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["Stop"].update({"coord": {"p": None, "t": None, "V": None, "I": None}})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["Stop"].update({"val": None})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["Stop"].update({"lim": None})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["Stop"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["CUP"]["Result"]["BT"].update({"INom": {}})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["INom"].update({"val": None})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["INom"].update({"lim": None})
        self.data_base["Test"]["CUP"]["Result"]["BT"]["INom"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["CUP"]["Result"].update({"Asd": {}})

        self.data_base["Test"]["CUP"]["Result"]["Asd"].update({"Start": {}})
        self.data_base["Test"]["CUP"]["Result"]["Asd"]["Start"].update({"coord": {"p": None, "t": None, "V": None, "I": None}})
        self.data_base["Test"]["CUP"]["Result"]["Asd"]["Start"].update({"val": None})
        self.data_base["Test"]["CUP"]["Result"]["Asd"]["Start"].update({"lim": None})
        self.data_base["Test"]["CUP"]["Result"]["Asd"]["Start"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["CUP"]["Result"]["Asd"].update({"Stop": {}})
        self.data_base["Test"]["CUP"]["Result"]["Asd"]["Stop"].update({"coord": {"p": None, "t": None, "V": None, "I": None}})
        self.data_base["Test"]["CUP"]["Result"]["Asd"]["Stop"].update({"val": None})
        self.data_base["Test"]["CUP"]["Result"]["Asd"]["Stop"].update({"lim": None})
        self.data_base["Test"]["CUP"]["Result"]["Asd"]["Stop"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["CUP"]["Result"]["Asd"].update({"INom": {}})
        self.data_base["Test"]["CUP"]["Result"]["Asd"]["INom"].update({"val": None})
        self.data_base["Test"]["CUP"]["Result"]["Asd"]["INom"].update({"lim": None})
        self.data_base["Test"]["CUP"]["Result"]["Asd"]["INom"].update({"status": self.warning["NA"]})

        # initialize the SBO data base
        self.data_base["Test"].update({"PSU": {}})
        self.data_base["Test"]["PSU"].update({"selected": None})
        self.data_base["Test"]["PSU"].update({"Path": None})
        self.data_base["Test"]["PSU"].update({"File": None})
        self.data_base["Test"]["PSU"].update({"Result": {}})
        self.data_base["Test"]["PSU"].update({"Setting": {}})
        self.data_base["Test"]["PSU"].update({"Time": None})

        self.data_base["Test"]["PSU"]["Setting"].update({"ChA_Scale": None})
        self.data_base["Test"]["PSU"]["Setting"].update({"ChB_Scale": None})
        self.data_base["Test"]["PSU"]["Setting"].update({"CMD": "PSU_test"})

        self.data_base["Test"]["PSU"]["Result"].update({"status": self.warning["NA"]})
        self.data_base["Test"]["PSU"]["Result"].update({"Analysis_status": None})
        self.data_base["Test"]["PSU"]["Result"].update({"Start_level": {}})
        self.data_base["Test"]["PSU"]["Result"]["Start_level"].update({"coord": {"p": None, "t": None, "V": None}})
        self.data_base["Test"]["PSU"]["Result"]["Start_level"].update({"val": None})

        self.data_base["Test"]["PSU"]["Result"].update({"High_Stop_level": {}})
        self.data_base["Test"]["PSU"]["Result"]["High_Stop_level"].update({"coord": {"p": None, "t": None, "V": None}})
        self.data_base["Test"]["PSU"]["Result"]["High_Stop_level"].update({"val": None})
        self.data_base["Test"]["PSU"]["Result"]["High_Stop_level"].update({"lim": None})
        self.data_base["Test"]["PSU"]["Result"]["High_Stop_level"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["PSU"]["Result"].update({"Restart_Level": {}})
        self.data_base["Test"]["PSU"]["Result"]["Restart_Level"].update({"coord": {"p": None, "t": None, "V": None}})
        self.data_base["Test"]["PSU"]["Result"]["Restart_Level"].update({"val": None})
        self.data_base["Test"]["PSU"]["Result"]["Restart_Level"].update({"lim": None})
        self.data_base["Test"]["PSU"]["Result"]["Restart_Level"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["PSU"]["Result"].update({"Low_Stop_Level": {}})
        self.data_base["Test"]["PSU"]["Result"]["Low_Stop_Level"].update({"coord": {"p": None, "t": None, "V": None}})
        self.data_base["Test"]["PSU"]["Result"]["Low_Stop_Level"].update({"val": None})
        self.data_base["Test"]["PSU"]["Result"]["Low_Stop_Level"].update({"lim": None})
        self.data_base["Test"]["PSU"]["Result"]["Low_Stop_Level"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["PSU"]["Result"].update({"Charging_Rise_Time": {}})
        self.data_base["Test"]["PSU"]["Result"]["Charging_Rise_Time"].update({"coord": {"p": None, "t": None, "V": None}})
        self.data_base["Test"]["PSU"]["Result"]["Charging_Rise_Time"].update({"val": None})
        self.data_base["Test"]["PSU"]["Result"]["Charging_Rise_Time"].update({"lim": None})
        self.data_base["Test"]["PSU"]["Result"]["Charging_Rise_Time"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["PSU"]["Result"].update({"Discharging_Fall_Time": {}})
        self.data_base["Test"]["PSU"]["Result"]["Discharging_Fall_Time"].update({"coord": {"p": None, "t": None, "V": None}})
        self.data_base["Test"]["PSU"]["Result"]["Discharging_Fall_Time"].update({"val": None})
        self.data_base["Test"]["PSU"]["Result"]["Discharging_Fall_Time"].update({"lim": None})
        self.data_base["Test"]["PSU"]["Result"]["Discharging_Fall_Time"].update({"status": self.warning["NA"]})

        # initialize the PWX data base
        self.data_base["Test"].update({"PWX": {}})
        self.data_base["Test"]["PWX"].update({"SubFolder": None})
        self.data_base["Test"]["PWX"].update({"selected": None})
        self.data_base["Test"]["PWX"].update({"Number": None})
        self.data_base["Test"]["PWX"].update({"Path": None})
        self.data_base["Test"]["PWX"].update({"File": None})
        self.data_base["Test"]["PWX"].update({"Result": {}})
        self.data_base["Test"]["PWX"].update({"Setting": {}})
        self.data_base["Test"]["PWX"].update({"Time": None})

        self.data_base["Test"]["PWX"]["Setting"].update({"ChA_Scale": None})
        self.data_base["Test"]["PWX"]["Setting"].update({"ChB_Scale": None})
        self.data_base["Test"]["PWX"]["Setting"].update({"CMD": "PWX_test"})

        self.data_base["Test"]["PWX"]["Result"].update({"Analysis_status": None})
        self.data_base["Test"]["PWX"]["Result"].update({"single_stats": {}})
        self.data_base["Test"]["PWX"]["Result"].update({"sum_stats": {}})
        self.data_base["Test"]["PWX"]["Result"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["PWX"]["Result"]["single_stats"].update({"shot_index": None, "t_stamp": None, "Iinv": None, "Ibr": None, "Vbr": None, "Power": None, "Charge": None, "Capa": None, "dtime": None})

        self.data_base["Test"]["PWX"]["Result"]["sum_stats"].update({"Median_Vbr": {}})
        self.data_base["Test"]["PWX"]["Result"]["sum_stats"]["Median_Vbr"].update({"val": None})
        self.data_base["Test"]["PWX"]["Result"]["sum_stats"]["Median_Vbr"].update({"lim": None})
        self.data_base["Test"]["PWX"]["Result"]["sum_stats"]["Median_Vbr"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["PWX"]["Result"]["sum_stats"].update({"Jitter_Vbr": {}})
        self.data_base["Test"]["PWX"]["Result"]["sum_stats"]["Jitter_Vbr"].update({"val": None})
        self.data_base["Test"]["PWX"]["Result"]["sum_stats"]["Jitter_Vbr"].update({"lim": None})
        self.data_base["Test"]["PWX"]["Result"]["sum_stats"]["Jitter_Vbr"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["PWX"]["Result"]["sum_stats"].update({"Median_Ibr": {}})
        self.data_base["Test"]["PWX"]["Result"]["sum_stats"]["Median_Ibr"].update({"val": None})
        self.data_base["Test"]["PWX"]["Result"]["sum_stats"]["Median_Ibr"].update({"lim": None})
        self.data_base["Test"]["PWX"]["Result"]["sum_stats"]["Median_Ibr"].update({"status": self.warning["NA"]})

        self.data_base["Test"]["PWX"]["Result"]["sum_stats"].update({"Median_dtime": {}})
        self.data_base["Test"]["PWX"]["Result"]["sum_stats"]["Median_dtime"].update({"val": None})
        self.data_base["Test"]["PWX"]["Result"]["sum_stats"]["Median_dtime"].update({"lim": None})
        self.data_base["Test"]["PWX"]["Result"]["sum_stats"]["Median_dtime"].update({"status": self.warning["NA"]})

        # initialize the PWX data base
        self.data_base["Test"].update({"Report": {}})
        self.data_base["Test"]["Report"].update({"selected": None})
        self.data_base["Test"]["Report"].update({"Path": None})
        self.data_base["Test"]["Report"].update({"File": None})

        self.data_base["Live_SBO"].update(copy.deepcopy(self.data_base["Test"]["SBO"]))
