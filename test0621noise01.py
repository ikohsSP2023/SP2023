import keyboard
import sounddevice as sd
import soundfile as sf
import threading
import numpy as np

duration = 1.5  # 3秒間再生する

output_device_info = sd.query_devices(device=sd.default.device[1])

f0 = 440
offset = 0
sr_out = int(output_device_info["default_samplerate"])

mode = "continue"

filepath = "./laser_noise0613_trim01.wav"
sig, sr = sf.read(filepath, always_2d=True)

n_samples, n_channels = sig.shape
blocksize = 1024
current_frame = 0

def callback(outdata, frames, time, status):
    global sr_out, offset, f0, mode, current_frame, n_samples, n_channels, sig
    n_channels = 2
    # n_samples, n_channels = outdata.shape

    chunksize = min(n_samples - current_frame, frames)
    outdata[:] *= 0.0


    for k in range(n_channels):
        # outdata[0:chunksize, k] = sig[current_frame:current_frame + chunksize, k]
        outdata[0:chunksize, k] = sig[current_frame:current_frame + chunksize, 0]

    # t = np.arange(offset, offset+n_samples) / sr_out
    # for k in range(n_channels):
    #     outdata[:, k] = np.sin(2*np.pi*f0*t) / n_channels
    
    if mode == "mono":
        outdata[:, 1] = 0.0 * sig[current_frame:current_frame + chunksize, 0] 

    if mode == "inv":
        outdata[:, 1] = -1.0 * sig[current_frame:current_frame + chunksize, 0]

    # offset += n_samples


    if chunksize < frames:
        raise sd.CallbackStop()

    current_frame += chunksize

def keyPressed(key):
    global mode
    if key == "space":
        mode = "quit"
    if key == "a":
        mode = "inv"
    if key == "b":
        mode = "mono"
    if key == "c":
        mode = "stereo"

key1 = "space"
keyboard.add_hotkey(key1, keyPressed, (key1, ))
key2 = "a"
keyboard.add_hotkey(key2, keyPressed, (key2, ))
key3 = "b"
keyboard.add_hotkey(key3, keyPressed, (key3, ))
key4 = "c"
keyboard.add_hotkey(key4, keyPressed, (key4, ))

steram = sd.OutputStream(
    samplerate = sr,
    blocksize = blocksize,
    # channels=sig.shape[1], 
    channels=2, 
    dtype='float32', 
    callback=callback
)

with steram:
    a = input("stop")
