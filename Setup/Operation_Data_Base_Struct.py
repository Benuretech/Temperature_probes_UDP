"""
Database structure definition for Operation system with operational data management initialization.
"""

from Setup.Limit_Check import LimitCheck

class Operation_Data_Base_Struct:
    def __init__(self):
        
        self.limit_check_obj = LimitCheck()
        self.warning=self.limit_check_obj.warning
        

        #initialize the data base
        self.data_base={}
        #initialize the Excel data base
        self.data_base.update({"ConfigBase":{}})

        self.data_base.update({"MCU":{}})       
        self.data_base.update({"PICO":{}})


        self.data_base["PICO"].update({"picoscope_model":False})             
        self.data_base["PICO"].update({"picoscope_ready":False})    # Picoscope ready flag
        self.data_base["PICO"].update({"Task":"Wait"}) # Task being executed, "PWX_test"/"PSU_test"/ "Wait" for no task
        self.data_base["PICO"].update({"Status":"Stop"})  # Task status, "Run"/"Stop"/"terminate"/"Done"/"Time_Out"/"Shot"
        self.data_base["PICO"].update({"Result":{}})  #Time of the PSU test start
  



        self.data_base.update({"CMD":{}})          
        #initialize the Job data base
        self.data_base.update({"Operation":{}})

        

        #initialize the SBO data base
        self.data_base["Operation"].update({"OPCheck_List":[]}) 


        self.data_base["Operation"].update({"SN_List":{}})
        self.data_base["Operation"]["SN_List"].update({"SBO":[]})
        self.data_base["Operation"]["SN_List"].update({"tooltype":[]})
        



        self.data_base.update({"Live_SBO":{}})

        #initialize the SBO data base
 
        self.data_base["Live_SBO"].update({"selected":None}) 
        self.data_base["Live_SBO"].update({"Path":None})  
        self.data_base["Live_SBO"].update({"File":None})     
        self.data_base["Live_SBO"].update({"Result":{}})

        self.data_base["Live_SBO"]["Result"].update({"status":self.warning["NA"]}) 

        #initialize the SBO test data base        

        self.data_base["Live_SBO"]["Result"].update({"I_Leackage":{}})
        self.data_base["Live_SBO"]["Result"].update({"R100":{}})
        self.data_base["Live_SBO"]["Result"].update({"R300":{}})
        self.data_base["Live_SBO"]["Result"].update({"V_Tolerance":{}})
        self.data_base["Live_SBO"]["Result"].update({"I_Tolerance":{}})        

        #initialize the Component SBO data base         
        self.data_base["Live_SBO"]["Result"].update({"RJ45_ST":{}})
        self.data_base["Live_SBO"]["Result"].update({"RS485_ST":{}})
        self.data_base["Live_SBO"]["Result"].update({"CAL_ST":{}})
        self.data_base["Live_SBO"]["Result"].update({"PICO":{}})
        self.data_base["Live_SBO"]["Result"].update({"SSR_ST":{}})
 
        self.data_base["Live_SBO"]["Result"].update({"VERSION": {"val": None, "status": self.warning["NA"]}})

        #initialize the limit SBO calibration data base      
        self.data_base["Live_SBO"]["Result"]["I_Leackage"].update({"lim":{"unit": "V","LL": -0.01,"L": -0.0099,"H": 0.0099,"HH": 0.01}})        
        self.data_base["Live_SBO"]["Result"]["R100"].update({"lim":{"unit": "Ohms","LL": 95,"L": 96,"H": 104,"HH": 105}}) 
        self.data_base["Live_SBO"]["Result"]["R300"].update({"lim":{"unit": "Ohms","LL": 295,"L": 296,"H": 304,"HH": 305}}) 
        self.data_base["Live_SBO"]["Result"]["V_Tolerance"].update({"lim":{"unit": "%","LL": -2,"L": -1.9,"H": 1.9,"HH": 2}}) 
        self.data_base["Live_SBO"]["Result"]["I_Tolerance"].update({"lim":{"unit": "%","LL": -2,"L": -1.9,"H": 1.9,"HH": 2}}) 


        #initialize the val SBO calibration data base      
        self.data_base["Live_SBO"]["Result"]["I_Leackage"].update({"val":None})        
        self.data_base["Live_SBO"]["Result"]["R100"].update({"val":None})
        self.data_base["Live_SBO"]["Result"]["R300"].update({"val":None})
        self.data_base["Live_SBO"]["Result"]["V_Tolerance"].update({"val":None})
        self.data_base["Live_SBO"]["Result"]["I_Tolerance"].update({"val":None})
        
        #initialize the status SBO calibration data base      
        self.data_base["Live_SBO"]["Result"]["I_Leackage"].update({"status":self.warning["NA"]})        
        self.data_base["Live_SBO"]["Result"]["R100"].update({"status":self.warning["NA"]})
        self.data_base["Live_SBO"]["Result"]["R300"].update({"status":self.warning["NA"]})
        self.data_base["Live_SBO"]["Result"]["V_Tolerance"].update({"status":self.warning["NA"]})
        self.data_base["Live_SBO"]["Result"]["I_Tolerance"].update({"status":self.warning["NA"]})


        #initialize the val SBO calibration data base      
        self.data_base["Live_SBO"]["Result"]["RJ45_ST"].update({"val":None})        
        self.data_base["Live_SBO"]["Result"]["RS485_ST"].update({"val":None})
        self.data_base["Live_SBO"]["Result"]["CAL_ST"].update({"val":None})
        self.data_base["Live_SBO"]["Result"]["PICO"].update({"val":None})
        self.data_base["Live_SBO"]["Result"]["SSR_ST"].update({"val":None})
   



