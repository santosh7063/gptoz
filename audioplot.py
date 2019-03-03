#!/usr/bin/env python3
import sys
import numpy as np
import scipy.fftpack
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from audiopack import loadwav


try:
    soundfile = sys.argv[1]
except IndexError:
    print("no audiofile provided")
    sys.exit()
else:
    try:
        mode = sys.argv[2]
    except IndexError:
        mode = 'freq'

meta, data = loadwav(soundfile)

t = np.linspace(0, meta.seconds, meta.samples)
print("Samplerate: %d" % meta.rate)
print("Channels: %d" % meta.channels)
print("Length: %d samples, %d seconds" % (meta.samples, meta.seconds))

fig = plt.figure()
gs = gridspec.GridSpec(meta.channels, 1)

# time/signal view
if mode == 'freq':
    for i, channel in enumerate(data.T):
        ax = plt.Subplot(fig, gs[i])
        ax.plot(t, channel)
        fig.add_subplot(ax)

# frequency/energy view
elif mode[:4] == 'spec':
    N = meta.samples
    T = 1.0 / meta.samples * 1.25
    x = np.linspace(0.0, 1.0/(2.0*T), N/2)
    for i, channel in enumerate(data.T):
        y = scipy.fftpack.fft(channel)
        ax = plt.Subplot(fig, gs[i])
        ax.plot(x, 2.0/N * np.abs(y[:N/2]))
        fig.add_subplot(ax)

plt.show()
plt.close()
