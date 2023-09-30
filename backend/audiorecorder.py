import pyaudio
import audioop
import numpy as np
from threading import Thread, Event
from queue import Queue
import time

FORMAT = pyaudio.paInt16  # 16 bits per sample
CHANNELS = 1 # Record in mono
VOLUME_THRESHOLD = 1000
RATE = 44100
CHUNK = 0


class AudioRecorder():

    def __init__(self):
        self.event = Event()
        self.t_main = None


    def record(self):
        p = pyaudio.PyAudio()  # Create an interface to PortAudio

        # Print audio devices to console
        info = p.get_host_api_info_by_index(0)

        INPUT_DEVICE = 1

        numdevices = info.get('deviceCount')

        for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print ("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

        stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index = INPUT_DEVICE)  # Input device

        while True:

            if self.event.is_set():
                break

            data = stream.read(CHUNK)   # Read a chunk of data from the stream

            data_int = np.frombuffer(data, dtype=np.int16)   # Convert data to int16

            volume = audioop.rms(data, 2)  # Store volume of chunk
        
        stream.close()
        p.terminate()


    def startRecording(self):
        self.q_data = Queue()
        self.t_main = Thread(target=self.record)
        self.t_main.start()
        
        print("\naudiorecorder.py: Starting recording...\n")


    def stopRecording(self):
        self.event.set()

        if self.t_main != None:
            self.t_main.join()
        
        self.event.clear()
        print("\naudiorecorder.py: Stopping recording...\n")
