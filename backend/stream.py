import sounddevice as sd
import argparse
import numpy
assert numpy

class AudioStream(object):
    def __init__(self, rate, block, channels, latency, input_device, output_device):
        self.parser = argparse.ArgumentParser(add_help=False)
        self.rate = rate
        self.block = block
        self.channels = channels
        self.latency = latency
        self.input_device = input_device
        self.output_device = output_device
        self.circular_buffer = numpy.zeros((rate, channels))
        self.buffer_index = 0
        print(sd.query_devices())

    def echo(self, input_signal, delay, decay):
        delay_samples =int(delay * self.rate)
        num_samples = len(input_signal)
        output_signal = numpy.zeros_like(input_signal)

        for i in range(num_samples):
            delayed_index = (self.buffer_index - delay_samples) % self.rate
            output_signal[i] = input_signal[i] + self.circular_buffer[delayed_index] * decay
            self.circular_buffer[self.buffer_index] = input_signal[i]
            self.buffer_index = (self.buffer_index + 1) % self.rate

        return output_signal

    def callback(self, indata, outdata, frames, time, status):
        if status:
            print(status)
        
        # Echo
        # outdata[:] = self.echo(indata, 0.5, 0.4)

        outdata[:] = indata

    def stream(self):
        try :
            with sd.Stream(device=(self.input_device, self.output_device), 
                        samplerate=self.rate, 
                        blocksize=self.block, 
                        latency=self.latency, 
                        channels=self.channels, 
                        callback=self.callback):
                print('press ENTER to quit')
                input()
        except KeyboardInterrupt:
            self.parser.exit('')
