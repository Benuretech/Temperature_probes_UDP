"""
Data validation utility that checks values against predefined limits with color-coded status indicators.
It returns a dictionary which contains the result of the check, including
status messages (Good, Fail, Warning, etc.) and colors based on the results of these checks.
"""

class LimitCheck:
    """Class for checking data against predefined limits and managing associated states."""
    
    def __init__(self):
        self.warning = {
            "HH": {"color": "background-color: #ff2600","color_code": "#ff2600", "message": "Fail", "level": 3, "Accept": False,"key":"HH","abs_level":3},
            "LL": {"color": "background-color: #ff2600","color_code": "#ff2600", "message": "Fail", "level": -3, "Accept": False,"key":"LL","abs_level":3}, 
            "H": {"color": "background-color: #ffd479","color_code": "#ffd479", "message": "Warning", "level": 2, "Accept": True,"key":"H","abs_level":2},           
            "L": {"color": "background-color: #ffd479","color_code": "#ffd479", "message": "Warning", "level": -2, "Accept": True,"key":"L","abs_level":2},
            "pass": {"color": "background-color: #8efa00","color_code": "#8efa00", "message": "Good", "level": 1, "Accept": True,"key":"pass","abs_level":1},
            "NA": {"color": "background-color: #f0f0f0","color_code": "#f0f0f0", "message": "NA", "level": 0, "Accept": False,"key":"NA","abs_level":0},            
            3: {"color": "background-color: #ff2600","color_code": "#ff2600", "message": "Fail", "level": 3, "Accept": False,"key":"HH","abs_level":3},
            -3: {"color": "background-color: #ff2600","color_code": "#ff2600", "message": "Fail", "level": -3, "Accept": False,"key":"LL","abs_level":3}, 
            2: {"color": "background-color: #ffd479","color_code": "#ffd479", "message": "Warning", "level": 2, "Accept": True,"key":"H","abs_level":2},           
            -2: {"color": "background-color: #ffd479","color_code": "#ffd479", "message": "Warning", "level": -2, "Accept": True,"key":"L","abs_level":2},
            1: {"color": "background-color: #8efa00","color_code": "#8efa00", "message": "Good", "level": 1, "Accept": True,"key":"pass","abs_level":1},
            0: {"color": "background-color: #f0f0f0","color_code": "#f0f0f0", "message": "NA", "level": 0, "Accept": False,"key":"NA","abs_level":0} 

        }

        self.test_status = {                     
            3: {"color": "background-color: #ffd479","color_code": "#ffd479", "message": "Busy", "level": 3},       
            2: {"color": "background-color: #ff2600","color_code": "#ff2600", "message": "Fail", "level": 2},       
            1: {"color": "background-color: #8efa00","color_code": "#8efa00", "message": "Good", "level": 1},
            0: {"color": "background-color: #f0f0f0","color_code": "#f0f0f0", "message": "NA", "level": 0} 

        }


    def value_check(self, data_dict):
        """Check the value against limits and return the corresponding key."""
        data_val = data_dict["val"]

        if data_val in ["", "NA"]:
            return "NA"

        data_val = float(data_val)       

        if data_val > data_dict["lim"]["HH"]:
            return "HH"
        elif data_val > data_dict["lim"]["H"]:
            return "H"
        elif data_val < data_dict["lim"]["LL"]:
            return "LL"
        elif data_val < data_dict["lim"]["L"]:
            return "L"
        else:
            return "pass"

    def level_check(self, data_dict):
        """Return warning details based on the data level."""
        data_val = data_dict["val"]

        if data_val in ["", "NA", None]:
            return self.warning[0]

        data_val = float(data_val)       

        if data_val > data_dict["lim"]["HH"]:
            return self.warning[3]
        elif data_val > data_dict["lim"]["H"]:
            return self.warning[2]
        elif data_val < data_dict["lim"]["LL"]:
            return self.warning[-3]
        elif data_val < data_dict["lim"]["L"]:
            return self.warning[-2]
        else:
            return self.warning[1]

    def state_check(self, data_dict):
        """Return state based on value provided."""
        data_val = data_dict["val"]

        if data_val in ["", "NA", None]:
            return self.warning[0]

        elif data_val == 1:
            return self.warning[1]

        return self.warning[3]

    def state_check2(self, value):
        if value==None:
            return self.test_status[0]

        return self.test_status[value]

