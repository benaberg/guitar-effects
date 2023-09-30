import audiorecorder
import keyboard


audioRecorder = audiorecorder.AudioRecorder()
audioRecorder.startRecording()

while True:
    if keyboard.is_pressed("q"):
        audioRecorder.stopRecording()
        break