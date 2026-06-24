import numpy as np
WINDOWS = {
    5: np.hanning(5).astype(np.float32),
    7: np.hanning(7).astype(np.float32),
    9: np.hanning(9).astype(np.float32),
    21: np.hanning(21).astype(np.float32),
}
for k in WINDOWS:
    WINDOWS[k] /= WINDOWS[k].sum()

import wave
import struct

# ---------------------------------------------------------
# 1. Wygładzanie sygnału (Hanning)
# ---------------------------------------------------------

def smooth_audio(signal, window_size=7):
    """
    Wygładzanie sygnału audio za pomocą okna Hanninga i konwolucji.
    """
    signal = np.array(signal, dtype=np.float32)
    if window_size < 3:
        return signal
   window = WINDOWS.get(window_size)
    if window is None:
    window = np.hanning(window_size).astype(np.float32)
    window /= window.sum()

    return np.convolve(signal, window, mode='same')


# ---------------------------------------------------------
# 2. Łagodzenie ostrych pików
# ---------------------------------------------------------

def soften_peaks(signal, threshold=0.8, reduction=0.5):
    """
    Łagodzenie ostrych pików powyżej progu.
    """
    signal = np.array(signal, dtype=np.float32)
    peaks = np.abs(signal) > threshold
    signal[peaks] *= reduction
    return signal


# ---------------------------------------------------------
# 3. Tryby przetwarzania
# ---------------------------------------------------------

def human_friendly(signal):
    """
    Tryb 'dla ludzi' – miękkie wygładzenie i redukcja ostrych elementów.
    """
    s = smooth_audio(signal, window_size=9)
    s = soften_peaks(s, threshold=0.7, reduction=0.6)
    return s


def ultra_soft(signal):
    """
    Tryb ULTRA miękki – maksymalne wygładzenie dla bardzo wrażliwych uszu.
    """
    s = smooth_audio(signal, window_size=21)
    s = soften_peaks(s, threshold=0.5, reduction=0.4)
    return s


def speech_clarity(signal):
    """
    Tryb poprawiający zrozumiałość mowy.
    """
    s = smooth_audio(signal, window_size=5)
    s = soften_peaks(s, threshold=0.85, reduction=0.7)
    s = s * 1.1
    s = np.clip(s, -1.0, 1.0)   # zabezpieczenie przed przesterem
    return s


def auto_for_humans(signal):
    """
    Automatyczny tryb – wybiera UltraSoft lub SpeechClarity
    w zależności od ostrości sygnału i impulsów.
    """
    signal = np.array(signal, dtype=np.float32)
    diff = np.diff(signal)

    sharpness = np.mean(np.abs(diff))
    peak_sharpness = np.max(np.abs(diff))

    if sharpness > 0.15 or peak_sharpness > 1.5:
        return ultra_soft(signal)
    else:
        return speech_clarity(signal)


# ---------------------------------------------------------
# 4. Obsługa WAV
# ---------------------------------------------------------

def load_wav(path):
    """
    Wczytuje plik WAV i zwraca (signal, sample_rate).
    """
    with wave.open(path, 'rb') as w:
        channels = w.getnchannels()
        framerate = w.getframerate()
        frames = w.getnframes()
        raw = w.readframes(frames)

        fmt = "<" + "h" * (len(raw) // 2)
        data = struct.unpack(fmt, raw)

        if channels == 2:
            data = data[::2]

        signal = np.array(signal, dtype=np.float32)
        return signal, framerate


def save_wav(path, signal, framerate):
    """
    Zapisuje sygnał float (-1..1) do pliku WAV mono.
    """
    data = (np.array(signal) * 32767).astype(np.int16)

    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(framerate)

        raw = struct.pack("<" + "h" * len(data), *data)
        w.writeframes(raw)


# ---------------------------------------------------------
# 5. Pipeline: load → process → save
# ---------------------------------------------------------

def process_file(input_path, output_path, mode="human"):
    """
    Pełny pipeline: wczytaj → przetwórz → zapisz.
    mode: 'human', 'ultra', 'speech', 'auto'
    """
    signal, rate = load_wav(input_path)

    if mode == "human":
        processed = human_friendly(signal)
    elif mode == "ultra":
        processed = ultra_soft(signal)
    elif mode == "speech":
        processed = speech_clarity(signal)
    elif mode == "auto":
        processed = auto_for_humans(signal)
    else:
        processed = signal

    save_wav(output_path, processed, rate)
