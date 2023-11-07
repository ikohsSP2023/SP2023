import pyaudio
import sys
import time
import wave

import sounddevice as sd
import soundfile as sf

import matplotlib as mpl
mpl.use('TkAgg')

import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

from world import main

vocoder = main.World()

CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 1


myrecording = sd.rec(int(RECORD_SECONDS * RATE), samplerate = RATE, channels=CHANNELS)
sd.wait()
myrecording = myrecording.T
myrecording = np.squeeze(myrecording)

dat = vocoder.encode(RATE, myrecording, f0_method='harvest')
dat = vocoder.decode(dat)

xx = np.linspace(0, RATE/2, dat['spectrogram'][:, 1].size)

plt.figure(figsize=(15, 3))
plt.plot(myrecording)
plt.show()
plt.figure(figsize=(15, 3))

plt.plot(xx, np.log(np.abs(dat['spectrogram'][:, 10])))
plt.show()

plt.figure(figsize=(15, 3))
plt.plot((dat['out'] * 2 ** 15).astype(np.int16))
plt.show()