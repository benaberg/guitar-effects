import sounddevice as sd
import librosa
import time as t
import recorder
import argparse
import numpy
from cython_files import c_echo, c_overdrive, c_pitch_shift
assert numpy

class AudioStream(object):
    def __init__(self, rate, block, delay, channels, latency, input_device, output_device, record):
        self.parser = argparse.ArgumentParser(add_help=False)
        self.rate = rate
        self.block = block
        self.channels = channels
        self.latency = latency
        self.input_device = input_device
        self.output_device = output_device
        self.c_buffer_max = (int) (rate * delay)
        self.c_buffer = numpy.zeros((self.c_buffer_max, channels), dtype=numpy.float32)
        self.c_buffer_index = 0
        self.record = record
        self.recorder = recorder.AudioRecorder(self.rate)
        self.recording_left = [] # Store left channel audio
        self.recording_right = []  # Store right channel audio
        self.iter = 0
        self.mean = 0
        print(sd.query_devices())

    def overdrive(self, input_signal, gain, threshold):
        output_signal = numpy.tanh(input_signal * gain) * threshold

        return output_signal
    
    def echo(self, input_signal, delay, decay):
        delay_samples = int(delay * self.rate)
        num_samples = len(input_signal)
        output_signal = numpy.zeros_like(input_signal)
        i = 0

        while i < num_samples:
            delayed_index = (self.c_buffer_index - delay_samples) % self.c_buffer_max
            output_signal[i] = input_signal[i] + self.c_buffer[delayed_index]
            self.c_buffer[self.c_buffer_index] = input_signal[i] + decay * self.c_buffer[self.c_buffer_index]
            self.c_buffer_index = (self.c_buffer_index + 1) % self.c_buffer_max
            i += 1
        
        return output_signal

    def pitch_shift(self, input_signal, shift):
        target_sampling_rate = self.rate * shift
        stretched_signal = self.time_stretch(input_signal, shift)
        resampled_signal = librosa.resample(stretched_signal, orig_sr=self.rate, target_sr=target_sampling_rate * 2)

        ### START FILTER

        # Create two signals phase-shifted by 180 degrees
        signal1 = resampled_signal[::2]
        signal2 = resampled_signal[1::2]
        
        # Modulate amplitude using triangular distribution
        fade_in = numpy.linspace(0, 1, len(signal1) // 2)
        fade_out = numpy.linspace(1, 0, len(signal1) // 2)
        fade = numpy.concatenate((fade_in, fade_out))
        
        signal1 *= fade
        signal2 *= fade[::-1]  # Reverse fade for second signal

        output_signal = signal1 + signal2
        

        return output_signal

        ### END FILTER

    def time_stretch(self, input_signal, stretch_factor):
        output_signal = librosa.effects.time_stretch(input_signal, rate=stretch_factor)
        
        return output_signal
    
    def writeRecording(self, data): 
        self.recorder.append(data)

    def callback(self, indata, outdata, frames, time, status):
        if status:
            print(status)

        gain = 120
        threshold = 0.03
        delay = 0.08
        decay = 0.4
    

        ### Overdrive

        # Python

        #outdata[:] = self.overdrive(indata, gain, threshold)
        #outdata[:,1] = outdata[:,0]

        # Cython
        #outdata[:] = c_overdrive.overdrive(indata, gain, threshold)
        #outdata[:,1] = outdata[:,0]


        ### Echo

        # Python
        #outdata[:] = self.echo(outdata, delay, decay)
        #outdata[:,1] = outdata[:,0]

        # Cython
        #outdata[:] = c_echo.echo(indata, delay, decay, self.rate, self.c_buffer, self.c_buffer_index, self.c_buffer_max, self.iter)
        #outdata[:,1] = outdata[:,0]


        ### Pitch shift

        # Python
        #outdata[:] = indata
        #outdata[:,1] = self.pitch_shift(indata[:,0], 0.5)  # 0.5 for one ocatave up

        # Cython
        #outdata[:] = indata
        #outdata[:,1] = c_pitch_shift.pitch_shift(indata[:,0], 0.5, self.rate)

        # Append audio to recorder
        if (self.record):
            for sample in outdata[:]:
                self.recording_left.append(sample[0])
                self.recording_right.append(sample[1])

    def stream(self):
        try :
            with sd.Stream(device=(self.input_device, self.output_device), 
                        samplerate=self.rate, 
                        blocksize=self.block, 
                        latency=self.latency, 
                        channels=self.channels, 
                        callback=self.callback,
                        dtype=numpy.float32):
                print('press ENTER to quit')
                input()
        except KeyboardInterrupt:
            self.parser.exit('')
        finally:
            if (self.record):
                self.recorder.write("recordings/recording.wav", self.recording_left, self.recording_right)
