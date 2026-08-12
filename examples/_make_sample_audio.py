"""Pomocnik: generuje przykladowy plik WAV do uzycia w przykladach.
Nie jest czescia biblioteki — tylko uzywany przez skrypty w examples/.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from easysound import save_wav

FS = 44100


def make_sample_wav(path, duration=2.0, fs=FS, seed=0):
    """Generuje sygnal przypominajacy nagranie mowy: nosna 220 Hz
    modulowana wolno + kilka ostrych trzaskow (symulacja szumu tla)."""
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    voice = 0.3 * np.sin(2 * np.pi * 220 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 2 * t))
    rng = np.random.default_rng(seed)
    hiss = rng.normal(0, 0.02, size=voice.shape)
    signal = voice + hiss

    # kilkanascie trzaskow/klikniec (np. szum nagrania terenowego)
    clicks = rng.choice(len(signal), size=15, replace=False)
    signal[clicks] += rng.choice([-1, 1], size=15) * 0.6

    save_wav(path, fs, signal)
    return fs, signal


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "sample_input.wav")
    make_sample_wav(out)
    print(f"Zapisano przykladowy plik: {out}")
