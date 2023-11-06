import sounddevice as sd
import soundfile as sf

import numpy as np

duration = 3

sd.default.device = [0, 1]
input_device_info = sd.query_devices(device=sd.default.device[1])
sr_in = int(input_device_info["default_samplerate"])

myrecording = sd.rec(int(duration * sr_in), samplerate = sr_in, channels=2)
sd.wait()

print(myrecording.shape)
sf.write("./myrecording.wav", myrecording, sr_in)