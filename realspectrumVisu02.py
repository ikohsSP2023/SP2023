import sounddevice as sd
import numpy as np

import matplotlib as mpl
mpl.use('TkAgg')


from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from scipy import signal


device_list = sd.query_devices()
print(device_list)

sd.default.device = [0, 1]

def callback(indata, frames, time, status):
    global plotdata
    data = indata[::downsample, 0]
    shift = len(data)
    plotdata = np.roll(plotdata, -shift, axis=0)
    plotdata[-shift:] = data

def update_plot(frame):
    global plotdata, window
    x = plotdata[-N:] * window
    F = np.fft.fft(x)
    F = F / (N / 2)
    F = F * (N / sum(window))
    Amp = np.abs(F)
    line.set_ydata(Amp[:N // 2])
    return line,

downsample = 1
length = int(1000 * 44100 / (1000 * downsample))
plotdata = np.zeros((length))
N = 2048
fs = 44100
window = signal.hann(N)
freq = np.fft.fftfreq(N, d=1 /fs)

fig, ax = plt.subplots()
line, = ax.plot(freq[:N // 2], np.zeros(N // 2))
ax.set_ylim([1, 0])
ax.set_xlim([0, 3000])
ax.set_xlabel('Frequency [Hz]')
ax.set_ylabel('Amplitude spectrum')
fig.tight_layout()

steram = sd.InputStream(
    channels = 1,
    dtype = 'float32',
    callback = callback
)
ani = FuncAnimation(fig, update_plot, interval = 30, blit = True)
with steram:
    plt.show()