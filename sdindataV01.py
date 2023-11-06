import sounddevice as sd
import numpy as np

sd.default.device = [0, 1]
duration = 10

def callback(indata, frames, time, status):
    print(indata.shape)

with sd.InputStream(
    channels = 1,
    dtype = 'float32',
    callback = callback
):
    sd.sleep(int(duration * 1000))