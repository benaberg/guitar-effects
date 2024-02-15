import sounddevice as sd
import argparse
import numpy
assert numpy

CHANNELS = 2
RATE = 48000
BLOCK = 1024
LATENCY = 0
INPUT_DEVICE = 20
OUTPUT_DEVICE = 20

class AudioStream():
    def __init__(self):
        self.parser = argparse.ArgumentParser(add_help=False)

    def callback(self, indata, outdata, frames, time, status):
        if status:
            print(status)
        
        outdata[:] = indata

    def stream(self):
        try :
            with sd.Stream(device=(INPUT_DEVICE, OUTPUT_DEVICE), 
                        samplerate=RATE, 
                        blocksize=BLOCK, 
                        latency=LATENCY, 
                        channels=CHANNELS, 
                        callback=self.callback):
                print('press ENTER to quit')
                input()
        except KeyboardInterrupt:
            self.parser.exit('')
