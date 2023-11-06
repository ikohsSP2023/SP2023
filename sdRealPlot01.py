import sounddevice as sd
import numpy as np

import matplotlib as mpl
mpl.use('TkAgg')

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

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
    global plotdata
    line.set_ydata(plotdata)
    return line,


downsample = 1
length = int(1000 * 44100 / (1000 * downsample))

plotdata = np.zeros((length))

fig, ax = plt.subplots()
line, = ax.plot(plotdata)
ax.set_ylim([-1.0, 1.0])
ax.yaxis.grid(True)
fig.tight_layout()

stream = sd.InputStream(
    channels=1,
    dtype='float32',
    callback = callback
)
ani = FuncAnimation(fig, update_plot, interval=30, blit=True)
with stream:
    plt.show()