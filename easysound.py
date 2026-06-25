import numpy as np
from scipy.io import wavfile
from scipy.signal import hann, convolve


# -----------------------------
# Walidacja wejścia
# -----------------------------
def _validate_signal(signal):
    if signal is None:
        raise ValueError("Signal is None.")
    signal = np.asarray(signal, dtype=float)
    if signal.ndim != 1:
        raise ValueError("Signal must be 1‑D array.")
    return signal


# -----------------------------
# Podstawowe wygładzanie (Hann)
# -----------------------------
def smooth_audio(signal, window_size=51):
    signal = _validate_signal(signal)
    if window_size < 3:
        return signal
    window = hann(window_size)
    window /= window.sum()
    return convolve(signal, window, mode="same")


# -----------------------------
# Redukcja pików (impulse softener)
# -----------------------------
def soften_peaks(signal, threshold=0.85, reduction=0.25):
    signal = _validate_signal(signal)
    out = signal.copy()
    peaks = np.where(np.abs(out) > threshold)[0]
    out[peaks] *= reduction
    return out


# -----------------------------
# Tryb human_friendly
# (łagodne wygładzanie + lekka redukcja pików)
# -----------------------------
def human_friendly(signal):
    s = smooth_audio(signal, window_size=41)
    return soften_peaks(s, threshold=0.88, reduction=0.55)


# -----------------------------
# ultra_soft
# (maksymalne wygładzanie)
# -----------------------------
def ultra_soft(signal):
    return smooth_audio(signal, window_size=121)


# -----------------------------
# speech_clarity
# (zachowuje ostre składowe mowy)
# -----------------------------
def speech_clarity(signal):
    signal = _validate_signal(signal)
    # lekkie wygładzanie + wzmocnienie transjentów
    s = smooth_audio(signal, window_size=21)
    transients = signal - s
    return s + 0.35 * transients


# -----------------------------
# Detekcja impulsów (poprawiona)
# -----------------------------
def _has_impulses(signal):
    # impuls = nagły skok > 4.5 * mediana energii lokalnej
    energy = np.abs(signal)
    med = np.median(energy)
    if med == 0:
        return False
    return np.any(energy > med * 4.5)


# -----------------------------
# auto_for_humans
# -----------------------------
def auto_for_humans(signal):
    signal = _validate_signal(signal)

    if _has_impulses(signal):
        return soften_peaks(signal)

    # jeśli nie ma impulsów → wybór wg crest factor
    crest = np.max(np.abs(signal)) / (np.mean(np.abs(signal)) + 1e-9)

    if crest < 2.0:
        return ultra_soft(signal)
    if crest < 3.0:
        return human_friendly(signal)
    return smooth_audio(signal)
    

# -----------------------------
# Obsługa WAV
# -----------------------------
def load_wav(path):
    sr, data = wavfile.read(path)
    data = data.astype(float)
    if data.ndim > 1:
        data = data.mean(axis=1)
    data /= np.max(np.abs(data)) + 1e-9
    return sr, data


def save_wav(path, sr, data):
    data = np.asarray(data)
    data = data / (np.max(np.abs(data)) + 1e-9)
    wavfile.write(path, sr, (data * 32767).astype(np.int16))


# -----------------------------
# process_file
# -----------------------------
def process_file(input_path, output_path, mode="auto"):
    sr, data = load_wav(input_path)

    if mode == "auto":
        out = auto_for_humans(data)
    elif mode == "soften_peaks":
        out = soften_peaks(data)
    elif mode == "human_friendly":
        out = human_friendly(data)
    elif mode == "ultra_soft":
        out = ultra_soft(data)
    elif mode == "speech_clarity":
        out = speech_clarity(data)
    elif mode == "smooth":
        out = smooth_audio(data)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    save_wav(output_path, sr, out)
    return out
