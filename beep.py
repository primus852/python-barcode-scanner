import threading
import winsound


class MakeBeep(threading.Thread):

    def __init__(self, sound_type):
        threading.Thread.__init__(self)
        self.sound_type = sound_type

    def run(self):

        frequency = 2500  # Default Frequency (Hertz)
        duration = 200  # Default Duration (ms)

        if self.sound_type == 'success':
            frequency = 1800
            duration = 200
            winsound.Beep(frequency, duration)
        if self.sound_type == 'duplicate':
            frequency = 1500
            duration = 1000
            winsound.Beep(frequency, duration)
        elif self.sound_type == 'fail':
            frequency = 2800
            duration = 100
            winsound.Beep(frequency, duration)
            winsound.Beep(frequency, duration)
            winsound.Beep(frequency, duration)
        else:
            winsound.Beep(frequency, duration)
