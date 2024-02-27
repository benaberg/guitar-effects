import soundfile as sf

class AudioRecorder(object):
    def __init__(self, rate):
        self.rate = rate

    def write(self, path, data):
        print("Writing data with length ", len(data))
        sf.write(path, data, self.rate)
