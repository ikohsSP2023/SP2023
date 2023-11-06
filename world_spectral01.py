import pyaudio
import sys
import time
import wave

import numpy as np
import matplotlib.pyplot as plt

from world import main

vocoder = main.World()

chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 1

p = pyaudio.PyAudio()

stream = p.open(
    format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    frames_per_buffer = chunk
)

all = []
for i in range(0, int(RATE/chunk*RECORD_SECONDS)):
    data = stream.read(chunk)
    all.append(data)

stream.close()
p.terminate()

data = b''.join(all)

x = np.frombuffer(data, dtype="int16")/32768.0
dat = vocoder.encode(RATE, x, f0_method='harvest')
dat = vocoder.decode(dat)

xx = np.linspace(0, RATE/2, dat['spectrogram'][:, 1].size)

# plt.figure(figsize=(15, 3))
# plt.plot(x)
# plt.show()
# plt.figure(figsize=(15, 3))
plt.plot(xx, np.log(np.abs(dat['spectrogram'][:, 10])))
plt.show()
# plt.figure(figsize=(15, 3))
# plt.plot((dat['out'] * 2 ** 15).astype(np.int16))
# plt.show()