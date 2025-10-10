"""
High-precision timer utility. Provides nanosecond-level timing accuracy in real-time applications requiring precise timing control.
"""

import time 

class Timer_Cycle:
    def __init__(self,update_rate):
        self.update_rate=update_rate*1000000
        self.lasttime=time.perf_counter_ns()+update_rate
        self.Active=True
    
    def run(self):
        if (self.Active==True):
            if ((time.perf_counter_ns()-self.lasttime)>self.update_rate):
                self.lasttime=time.perf_counter_ns()
                return True
            else: 
                return False
        else: 
            return False

    def reset(self):
        self.lasttime=time.perf_counter_ns()

