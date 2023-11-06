from tokenize import TokenInfo
import pyaudio
import sys
import time
import wave

import librosa
import numpy as np
import matplotlib.pyplot as plt
import tkinter

import matplotlib.animation as animation
from matplotlib.colors import Normalize

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from world import main

vocoder = main.World()

chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
# RECORD_SECONDS = 0.5
RECORD_SECONDS = 2

NUM_DATA_SHOWN = 100
EPSILON = 1e-10

SPECTRUM_MIN = -30
SPECTRUM_MAX = 0


p = pyaudio.PyAudio()
stream = p.open(
    format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    frames_per_buffer = chunk
)

all = []
for i in range(0, int(RATE / chunk * RECORD_SECONDS)):
    data = stream.read(chunk)
    all.append(data)

stream.close()
p.terminate()

data = b''.join(all)

x = np.frombuffer(data, dtype="int16") / 32768.0


dat = vocoder.encode(RATE, x, f0_method='dio')
dat = vocoder.decode(dat)

# size_shift = RATE/(1000*5)
size_shift = RATE/50

duration = dat['temporal_positions'][-1]
time_x_data = dat['temporal_positions']
MAX_NUM_SPECTROGRAM = dat['spectrogram'][:,0].size
freq_y_data = np.linspace(8000/MAX_NUM_SPECTROGRAM, 8000, MAX_NUM_SPECTROGRAM)
spectrogram_data = np.zeros((len(freq_y_data), len(time_x_data)))
spectrogram_data = np.log(np.abs(dat['spectrogram']))

X=np.zeros(spectrogram_data.shape)
Y=np.zeros(spectrogram_data.shape)

for idx_f, f_v in enumerate(freq_y_data):
    for idx_t, t_v in enumerate(time_x_data):
        X[idx_f, idx_t] = t_v
        Y[idx_f, idx_t] = f_v


root = tkinter.Tk()
root.wm_title("soundGUI")

frame1 = tkinter.Frame(root)
frame2 = tkinter.Frame(root)
frame1.pack(side="left")
frame2.pack(side="left")

fig, ax = plt.subplots()

canvas = FigureCanvasTkAgg(fig, master=frame1)
plt.xlabel('sec')
plt.ylabel('frequency [Hz]')

plt.imshow(
    np.flipud(spectrogram_data),
    extent=[0, duration, 0, 8000],
    aspect='auto',
    interpolation='nearest'
)

canvas.get_tk_widget().pack(side="left")

def _draw_spectrum(v):
    index = int((len(spectrogram_data[:, 0])-1)*(float(v)/duration))
    spectrum = spectrogram_data[index]

    plt.cla()
    x_data = np.linspace(0, RATE/2, len(spectrum))
    ax2.plot(x_data, spectrum)
    ax2.set_ylim(-30, 5)
    # ax2.set_xlim(0, RATE/2)
    ax2.set_xlim(0, 8000)
    ax2.set_ylabel('gain[dB]')
    ax2.set_xlabel('frequency [Hz]')
    canvas2.draw()

fig2, ax2 = plt.subplots()
canvas2 = FigureCanvasTkAgg(fig2, master=frame2)
canvas2.get_tk_widget().pack(side="top")


scale = tkinter.Scale(
    command=_draw_spectrum,
    master=frame2,
    from_=0,
    to=duration,
    # resolution=size_shift/RATE,
    resolution=0.004,
    label=u'スペクトルを表示する時間[sec]',
    orient=tkinter.HORIZONTAL,
    length=600,
    width=50,
    font=("",20)
)
scale.pack(side="top")

tkinter.mainloop()
