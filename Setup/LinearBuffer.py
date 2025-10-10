"""
A linear buffer with also ring buffer capabilities for real-time data storage and time-based data retrieval.
Provides efficient data buffering capabilities with support for multi-channel data streams, automatic
time indexing, and sliding window operations.
"""

from dvg_ringbuffer import RingBuffer
import numpy as np


# Explanation of the ring buffer and the indexing:
# initial state of the buffer (when the buffer hasn't been filled yet)


# Create a numpy array buffer that will store the data in a linear way
class LinearBuffer:
    def __init__(self, nb_lines, size_x, dt, ring):
        self.dt = dt  # time step

        # Buffer Dimensions
        self.size_line = nb_lines + 1  # number of lines (data channels) in the buffer + 1 for time
        self.max_array_size = int(size_x)  # maximum size of the buffer
        self.index = 0  # starting index of the buffer
        self.ring = ring  # ring buffer object

        # Linear Buffer?
        # self.np_array_x=np.zeros((1, self.max_array_size),dtype=int)   # numpy array that will store the data
        self.np_array = np.zeros((self.size_line, self.max_array_size), dtype=float)  # numpy array that will store the data
        self.np_array[0] = np.arange(0, self.max_array_size * self.dt, self.dt)  # first line of the buffer is the time

        # never used?
        # self.np_array_x=np.arange(0, self.max_array_size*self.dt, self.dt)    # first line of the buffer is the time
        self.np_slice = self.np_array  # slice of the buffer that will be used to display the data

        self.log_index = 0  # log index is the index of the total number of values that has been entered, it keeps going up even after crossing the ringbuffer boundary
        self.index_correction = 0
        self.rb_array = np.zeros((self.size_line, self.ring), dtype=float)  # numpy array that will store the data
        self.previous_start_index = 0
        self.rb_array_slice = np.zeros((self.size_line, self.ring), dtype=float)  # numpy array that will store the data

        # Ring Buffer
        self.rbX = RingBuffer(self.ring, dtype=np.float32, allow_overwrite=True)  # ring buffer for time
        self.rbA0 = RingBuffer(self.ring, dtype=np.float32, allow_overwrite=True)  # ring buffer for channel 1
        self.rbA1 = RingBuffer(self.ring, dtype=np.float32, allow_overwrite=True)  # ring buffer for channel 2

    #       self.rbX.extend(np.arange(0,self.ring*self.dt,self.dt,dtype=np.float32))
    #       self.rbA0.extend(np.zeros((self.ring,),dtype=np.float32))
    #       self.rbA1.extend(np.zeros((self.ring,),dtype=np.float32))

    # Clear the buffer
    def clear(self):
        self.log_index = 0
        self.previous_start_index = 0
        self.index_correction = 0
        self.rbX.clear()
        self.rbA0.clear()
        self.rbA1.clear()

    # Clear the buffer (identical to the above function??)
    def clear_full(self):
        self.log_index = 0
        self.previous_start_index = 0
        self.index_correction = 0
        self.rbX.clear()
        self.rbA0.clear()
        self.rbA1.clear()

    # Append data to the buffer
    def append_full_data(self, VA_input):
        lengthx = VA_input.shape[-1]  # length of the input
        self.np_array[:, self.log_index : self.log_index + lengthx] = VA_input  # append the data to the buffer including the time
        self.log_index = self.log_index + lengthx  # update the index

        self.np_slice = self.np_array[:, 0 : self.log_index]  # update the slice of the buffer

    # Append data to the buffer with the time based on the time step
    def RT_append_data(self, VA_input):  # append data to the buffer in real time?
        lengthVA = VA_input.shape[-1]  # length of the input
        if lengthVA < 1:
            return
        if len(self.rbX) < 1:
            start_x = 0
        else:
            start_x = self.rbX[-1] + self.dt

        stop_x = start_x + (lengthVA - 1) * self.dt

        self.log_index = self.log_index + lengthVA  # update the index

        self.rbX.extend(np.linspace(start_x, stop_x, num=lengthVA, dtype=np.float32))  # append the time to the buffer

        self.rbA0.extend(VA_input[0, :])  # append the data to the buffer
        self.rbA1.extend(VA_input[1, :])  # append the data to the buffer
        try:
            self.rb_array = np.array([self.rbX[:], self.rbA0[:], self.rbA1[:]])  # update the slice of the buffer
        except:
            print("error")

    # Append the data to the buffer including the time
    def RT_append_full_data(self, VA_input):

        self.log_index = self.log_index + VA_input.shape[-1]  # update the index

        self.rbX.extend(VA_input[0, :])  # append the time to the buffer
        self.rbA0.extend(VA_input[1, :])  # append the data to the buffer
        self.rbA1.extend(VA_input[2, :])  # append the data to the buffer
        self.rb_array = np.array([self.rbX[:], self.rbA0[:], self.rbA1[:]])  # update the slice of the buffer

    # return the last numbers of data from the ring buffer. The number of points returned is the "start"
    def slice_data(self, start):

        index_start = self.log_index - start
        return np.array([np.array(self.rbX[-index_start:]), np.array(self.rbA0[-index_start:]), np.array(self.rbA1[-index_start:])])  # update the slice of the buffer

    def rb_array_time(self, time_length):
        # Convert the ring buffers to numpy arrays for easier slicing

        time_array = np.array(self.rbX[:])

        ### load the previous start index (the next one should be close )
        previous_start_index = self.previous_start_index

        # Find the index where the time difference is greater than or equal to the time_length
        current_time = time_array[-1]  # The time of the last element in the ring buffer
        start_time = current_time - time_length  # The time of the first element in the 30 second slice

        # Find the index where time is greater than or equal to start_time
        indices = np.where(time_array >= start_time)[0]

        # Check if the time at the current `previous_start_index` is still within the desired time range
        if time_array[previous_start_index] < start_time:
            # If the current `previous_start_index` is too far in the past, search forward from this point
            indices = np.where(time_array[previous_start_index:] >= start_time)[0]
            if len(indices) == 0:
                return None  # No data for the given time length
            previous_start_index += indices[0]  # Adjust the `start_index` based on the search
        else:
            # If `start_index` is already within or too far into the future, search backward
            while previous_start_index > 0 and time_array[previous_start_index] > start_time:
                previous_start_index -= 1

            # Ensure that the `start_index` is the first one meeting the condition
            if time_array[previous_start_index] < start_time:
                previous_start_index += 1

        # Return the array in the same format as self.rb_array
        self.rb_array_slice = np.array([np.array(self.rbX[previous_start_index:]), np.array(self.rbA0[previous_start_index:]), np.array(self.rbA1[previous_start_index:])])

        # Update the `previous_start_index` for future calls
        self.previous_start_index = previous_start_index

        return self.rb_array_slice
