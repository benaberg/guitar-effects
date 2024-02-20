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
        print(sd.query_devices())

    def echo(seldf, indata, rate=192000, chunk=1024, delay=0.5, decay=0.5):
        
        indata = indata[:, 0]
        
        # Calculate delay in samples
        delay_samples = int(delay * 192000)

        # Initialize output array with zeros
        outdata = numpy.zeros_like(indata)

        # Iterate over the input signal in chunks of buffer_size
        for i in range(0, len(indata), chunk):
            # Extract a chunk of the input signal
            chunk = indata[i:i + chunk]

            # Create a delayed version of the chunk
            delayed_chunk = numpy.concatenate([numpy.zeros(delay_samples), chunk])

            # Apply decay to the delayed chunk
            decayed_chunk = delayed_chunk * decay

            # Add the decayed chunk to the output signal
            outdata[i:i + len(chunk)] += decayed_chunk

        return outdata

    def callback(self, indata, outdata, frames, time, status):
        if status:
            print(status)
        
        outdata[:] = indata
        #outdata[:] = self.echo(indata)

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
