# -*- coding: utf-8 -*-
from collections import namedtuple
from scipy.io import wavfile
from scipy.fftpack import fft
import numpy as np


"""
An audio-visualizing toolbox
"""

 ##     ##     ##      ##     ##     ##     ##     ##     ##
#  #  ##  #  ##  #  ##   #  ##  #  ##  #  ##  #  ##  #  ##  #  #
#   ##     ##     ##      ##     ##     ##     ##     ##     ##
##
### Audio data functions
##
#
def pcm2float(sig, dtype='float64'):
    """Convert PCM signal to floating point with a range from -1 to 1.
    Use dtype='float32' for single precision.
    Parameters
    ----------
    sig : array_like
        Input array, must have integral type.
    dtype : data type, optional
        Desired (floating point) data type.
    Returns
    -------
    numpy.ndarray
        Normalized floating point data.
    See Also
    --------
    float2pcm, dtype
    """
    sig = np.asarray(sig)
    if sig.dtype.kind not in 'iu':
        raise TypeError("'sig' must be an array of integers")
    dtype = np.dtype(dtype)
    if dtype.kind != 'f':
        raise TypeError("'dtype' must be a floating point type")

    i = np.iinfo(sig.dtype)
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max
    return (sig.astype(dtype) - offset) / abs_max


def loadwav(filename):
    rate, raw = wavfile.read(filename)
    data = pcm2float(raw, 'float64')
    meta = namedtuple('meta', ['rate', 'samples', 'seconds', 'channels'])
    meta.samples = len(data)
    meta.seconds = float(meta.samples) / float(rate)
    meta.rate    = rate
    try:
        meta.channels = data.shape[1]
    except IndexError:
        meta.channels = 1
    return meta, data


def audio_chunks(data, blocksize):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(data), blocksize):
        block = data[i:i+blocksize]
        if len(block) < blocksize:
            yield np.lib.pad(block, (0, blocksize-len(block)), 'constant')
        yield block


def spectrum(block, N, bins=None):
    s = 2.0/N * np.abs(fft(block)[:N//2])
    if bins is not None:
        r = []
        for i in range(bins):
            rel = len(s)//bins
            r.append(sum(s[i*rel: (i+1)*rel]))
        return r
    return s


def rms(block):
    return np.sqrt(np.sum(np.apply_along_axis(lambda x: x*x, 0, block)) / len(block))
