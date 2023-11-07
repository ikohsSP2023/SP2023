import sys
import time
import wave
import threading

import sounddevice as sd
import soundfile as sf

import matplotlib as mpl
mpl.use('TkAgg')

import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

import tkinter
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk
)

SAMPLING_RATE = 16000
FRAME_SIZE = 1024

SPECTRUM_MIN = -5
SPECTRUM_MAX = 1

VOLUME_MIN = -120
VOLUME_MAX = -10
EPSILON = 1e-10

hamming_window = np.hamming(FRAME_SIZE)
MAX_NUM_SPECTROGRAM = int(FRAME_SIZE / 2)
NUM_DATA_SHOWN = 100



def animate(frame_index):
    ax1_sub.set_array(spectrogram_data)
    ax2_sub.set_data(time_x_data, volume_data)

    return ax1_sub, ax2_sub


root = tkinter.Tk()
root.wm_title("SOUNDDEVICE_EXP4")

fig, ax1 = plt.subplots(1, 1)
canvas = FigureCanvasTkAgg(fig, master=root)

time_x_data = np.linspace(0, NUM_DATA_SHOWN * (FRAME_SIZE/SAMPLING_RATE), NUM_DATA_SHOWN)
freq_y_data = np.linspace(8000/MAX_NUM_SPECTROGRAM, 8000, MAX_NUM_SPECTROGRAM)

spectrogram_data = np.zeros((len(freq_y_data), len(time_x_data)))
volume_data = np.zeros(len(time_x_data))

X = np.zeros(spectrogram_data.shape)
Y = np.zeros(spectrogram_data.shape)
for idx_f, f_v in enumerate(freq_y_data):
    for idx_t, t_v in enumerate(time_x_data):
        X[idx_f, idx_t] = t_v
        Y[idx_f, idx_t] = f_v

ax1_sub = ax1.pcolormesh(
    X,
    Y,
    spectrogram_data,
    shading = 'nearest',
    cmap = 'jet',
    norm = Normalize(SPECTRUM_MIN, SPECTRUM_MAX)
)

ax2 = ax1.twinx()
ax2_sub, = ax2.plot(time_x_data, volume_data, c='y')

ax1.set_xlabel('sec')
ax1.set_ylabel('frequency[Hz]')
ax2.set_ylabel('volume [dB]')

ax2.set_ylim([VOLUME_MIN, VOLUME_MAX])

ani = animation.FuncAnimation(
    fig,
    animate,
    interval = 500,
    blit = True
)

toolbar = NavigationToolbar2Tk(canvas, root)
canvas.get_tk_widget().pack()

text = tkinter.StringVar()
text.set('0.0')
label = tkinter.Label(master=root, textvariable=text, font=("", 30))
label.pack()

def _quit():
    root.quit()
    root.destroy()

button = tkinter.Button(master=root, text="QUIT", command=_quit, font=("", 30))
button.pack()

def input_callback(in_data, frame_count, time_info, status_flags):
    global spectrogram_data, volume_data

    print(in_data.shape)
    x_current_frame = in_data[::downsample, 0]
    x_current_frame = x_current_frame.T
    print(x_current_frame.shape)
    # x_current_frame = np.frombuffer(in_data, dtype=np.float32)
    fft_spec = np.fft.rfft(x_current_frame * hamming_window)
    fft_log_abs_spec = np.log10(np.abs(fft_spec) + EPSILON)[:-1]

    spectrogram_data = np.roll(spectrogram_data, -1, axis=1)
    spectrogram_data[:, -1] = fft_log_abs_spec

    vol = 20*np.log10(np.mean(x_current_frame ** 2) + EPSILON)
    volume_data = np.roll(volume_data, -1)
    volume_data[-1] = vol

    return None


downsample = 1



stream = sd.InputStream(
    channels = 1,
    dtype = 'float32',
    samplerate = SAMPLING_RATE,
    blocksize=FRAME_SIZE,
    callback = input_callback
)

with stream:
    print("A")
    tkinter.mainloop()
    # sd.sleep(int(5 * 1000))
    # is_gui_running = True
    # is_gui_running = False
