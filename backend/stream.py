import sounddevice as sd
import recorder
import argparse
import numpy
assert numpy

class AudioStream(object):
    def __init__(self, rate, block, block_max, channels, latency, input_device, output_device, record):
        self.parser = argparse.ArgumentParser(add_help=False)
        self.rate = rate
        self.block = block
        self.channels = channels
        self.latency = latency
        self.input_device = input_device
        self.output_device = output_device
        self.c_buffer_max = rate * block_max
        self.c_buffer = numpy.zeros((self.c_buffer_max, channels))
        self.buffer_index = 0
        self.record = record
        self.recorder = recorder.AudioRecorder(self.rate)
        self.recording = []
        print(sd.query_devices())

    def overdrive(self, input_signal, gain, threshold):
        output_signal = numpy.tanh(input_signal * gain) * threshold

        return output_signal

    def echo(self, input_signal, delay, decay):
        delay_samples = int(delay * self.rate)
        num_samples = len(input_signal)
        output_signal = numpy.zeros_like(input_signal)

        for i in range(num_samples):
            delayed_index = (self.buffer_index - delay_samples) % self.c_buffer_max
            output_signal[i] = input_signal[i] + self.c_buffer[delayed_index] * decay
            self.c_buffer[self.buffer_index] = input_signal[i]
            self.buffer_index = (self.buffer_index + 1) % self.c_buffer_max

        return output_signal
    
    def writeRecording(self, data): 
        self.recorder.append(data)

    def callback(self, indata, outdata, frames, time, status):
        if status:
            print(status)


        # Overdrive
        gain = 10
        threshold = 0.5
        outdata[:] = self.overdrive(indata, gain, threshold)


        # Echo
        delay = 0.5
        decay = 0.5
        outdata[:] = self.echo(outdata, delay, decay)


        # Append audio to recorder
        if (self.record):
            for sample in outdata[:,0]:
                self.recording.append(sample)


        #outdata[:] = indata

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
                self.recorder.write("recordings/recording.wav", self.recording)
