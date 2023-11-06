import pyaudio
import numpy as np
import threading

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

import tkinter
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk
)

from pydub import AudioSegment
from pydub.utils import make_chunks

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
root.wm_title("EXP4-AUDIO-SAMPLE")

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
    shading='nearest',
    cmap='jet',
    norm = Normalize(SPECTRUM_MIN, SPECTRUM_MAX)
)

ax2 = ax1.twinx()

ax2_sub, = ax2.plot(time_x_data, volume_data, c='y')

ax1.set_xlabel('sec')
ax1.set_ylabel('frequency [Hz]')
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

button = tkinter.Button(master=root, text="終了", command=_quit, font=("", 30))
button.pack()

def input_callback(in_data, frame_count, time_info, status_flags):
    global spectrogram_data, volume_data
    x_current_frame = np.frombuffer(in_data, dtype=np.float32)
    fft_spec = np.fft.rfft(x_current_frame * hamming_window)
    fft_log_abs_spec = np.log10(np.abs(fft_spec) + EPSILON)[:-1]

    spectrogram_data = np.roll(spectrogram_data, -1, axis=1)
    spectrogram_data[:, -1] = fft_log_abs_spec

    vol = 20*np.log10(np.mean(x_current_frame ** 2) + EPSILON)
    volume_data = np.roll(volume_data, -1)
    volume_data[-1] = vol

    return None, pyaudio.paContinue

p = pyaudio.PyAudio()
stream = p.open(
    format = pyaudio.paFloat32,
    channels = 1,
    rate = SAMPLING_RATE,
    input = True,
    frames_per_buffer = FRAME_SIZE,
    stream_callback = input_callback
)

filename = './mp3/hotaruno_no_hikari.mp3'

audio_data = AudioSegment.from_mp3(filename)

p_play = pyaudio.PyAudio()
stream_play = p_play.open(
    format = p.get_format_from_width(audio_data.sample_width),
    channels = audio_data.channels,
    rate = audio_data.frame_rate,
    output = True
)

def play_music():
    global is_gui_running, text

    size_frame_music = 10
    idx = 0

    for chunk in make_chunks(audio_data, size_frame_music):
        if is_gui_running == False:
            break

        stream_play.write(chunk._data)
        now_sec = (idx * size_frame_music) / 1000.
        if is_gui_running:
            text.set('%.3f' % now_sec)

        idx += 1

t_play_music = threading.Thread(target=play_music)
t_play_music.setDaemon(True)
t_play_music.start()

is_gui_running = True
tkinter.mainloop()
is_gui_running = False
stream_play.stop_stream()
stream_play.close()
p_play.terminate()