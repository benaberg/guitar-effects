import stream

audioStream = stream.AudioStream(96000, 512, 0.08, 2, 0, 21, 21, True)
audioStream.stream()
