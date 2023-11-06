import sounddevice as sd
import soundfile as sf

import numpy as np

duration = 1.5

device_list = sd.query_devices()
print(device_list)

sd.default.device = [0, 1]
input_device_info = sd.query_devices(device=sd.default.device[1])
sr_in = int(input_device_info["default_samplerate"])
print(input_device_info["default_samplerate"])

# myrecording = sd.rec(int(duration * sr_in), samplerate = sr_in, channels=2)
# sd.wait()

# print(myrecording.shape)
# sf.write("./myrecording.wav", myrecording, sr_in)

# def callback(indata, outdata, frames, time, status):
#     n_samples, n_channels = outdata.shape
#     outdata[:] = indata

# with sd.Stream(
#     channels=2,
#     dtype='float32',
#     callback=callback
# ):
#     sd.sleep(int(duration*1000))