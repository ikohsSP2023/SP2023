import sounddevice as sd
import soundfile as sf

import numpy as np

device_list = sd.query_devices()
print(device_list)

for device_number in sd.default.device:
    print(device_number)
    print(device_list[device_number])