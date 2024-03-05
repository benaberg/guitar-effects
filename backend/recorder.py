import soundfile as sf
import numpy as np

class AudioRecorder(object):
    def __init__(self, rate):
        self.rate = rate

    def write(self, path, data_left, data_right):
        print("Writing data with length ", len(data_left))
        data = np.column_stack((data_left, data_right))
        
        sf.write(path, data, self.rate)
