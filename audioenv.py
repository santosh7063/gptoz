#!/usr/bin/env python3
import sys
import os
from functools import reduce
import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wavfile
from audiopack import pcm2float

"""
Plot envelope for an audio file
"""


try:
    soundfile = sys.argv[1]
except:
    print("no audiofile provided")
    sys.exit()

try:
    outfile = sys.argv[2]
except:
    outfile = "/tmp/%s.env" % os.path.basename(soundfile)

try:
    blocksize = sys.argv[3]
except:
    blocksize = 1764  # 25fps video-blocksize


# env = np.loadtxt('/tmp/rms.txt')
# x = np.arange(0, len(env));

rate, data = wavfile.read(soundfile)
print("Samplerate: %d" % rate)

# np.asarray(data).astype('float32') / 2 ** 15
# stangely casues
# OverflowError: Allocated too many blocks
# in np.plot with some files
#
# normalized = np.asarray(data).astype('float32') / 2 ** 16
normalized = pcm2float(data, "float64")

length = {}
length["samples"] = len(normalized)
length["seconds"] = length["samples"] / float(rate)
try:
    channels = data.shape[1]
except IndexError:
    channels = 1
print("Channels: %d" % channels)
print("Length: %d samples, %d seconds" % (length["samples"], length["seconds"]))

last_frame = length["samples"] // blocksize
frames = np.arange(0, last_frame)
env = [None] * channels

print("Calculating envelope ...")
for cnum, chan in enumerate(normalized.T):
    print("Channel %d" % cnum)
    env[cnum] = []
    for i in frames:
        env[cnum].append(
            reduce(
                lambda a, f: a + f * f, chan[i * blocksize : (i + 1) * blocksize], 0.0
            )
            / blocksize
        )

print("Done")

# fig = plt.figure()
# gs = gridspec.GridSpec(len(env), 1)

# plot channels
# for i, channel in enumerate(env):
#    ax = plt.Subplot(fig, gs[i])
#    ax.plot(frames, channel)
#    fig.add_subplot(ax)


for channel in env:
    plt.plot(frames, channel)

print("Writing to file: %s" % outfile)
with open(outfile, "w") as of:
    for f in frames:
        ch_frame = ["%6f" % env[i][f] for i in range(len(env))]
        # count frames from 1
        of.write("%05d %s\n" % ((f + 1), ", ".join(ch_frame)))

# np.savetxt(of, np.array(env), delimiter=",", newline=" ")
# export_env.tofile(outfile, sep=',', format='%10.5f')
# of.close()

plt.show()
plt.close()
