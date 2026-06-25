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
# smooth_audio z odbiciem krawędzi
# -----------------------------
def smooth_audio(signal, window_size=51):
    signal = _validate_signal(signal)
    if window_size < 3:
        return signal

    pad = window_size // 2
    padded = np.pad(signal, pad, mode="reflect")

    window = hann(window_size)
    window /= window.sum()

    smoothed = convolve(padded, window, mode="same")
    return smoothed[pad:-pad]


# -----------------------------
# soften_peaks — soft‑knee
# -----------------------------
def soften_peaks(signal, threshold=0.85, knee_width=0.15):
    signal = _validate_signal(signal)
    out = signal.copy()

    abs_sig = np.abs(out)
    over = abs_sig > threshold

    # soft knee: płynne przejście
    knee_end = threshold + knee_width
    in_knee = (abs_sig > threshold) & (abs_sig < knee_end)

    # część twarda
    out[abs_sig >= knee_end] = np.sign(out[abs_sig >= knee_end]) * knee_end

    # część miękka
    ratio = (abs_sig[in_knee] - threshold) / knee_width
    gain = 1 - ratio * 0.7  # 70% kompresji w kolanie
    out[in_knee] *= gain

    return out


# -----------------------------
# human_friendly
# -----------------------------
def human_friendly(signal):
    s = smooth_audio(signal, window_size=41)
    return soften_peaks(s, threshold=0.88, knee_width=0.12)


# -----------------------------
# ultra_soft
# -----------------------------
def ultra_soft(signal):
    return smooth_audio(signal, window_size=121)


# -----------------------------
# speech_clarity — transjenty ×0.65
# -----------------------------
def speech_clarity(signal):
    signal = _validate_signal(signal)
    s = smooth_audio(signal, window_size=21)
    transients = signal - s
    return s + 0.65 * transients


# -----------------------------
# Detekcja impulsów (poprawiona)
# -----------------------------
def _has_impulses(signal):
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

    crest = np.max(np.abs(signal)) / (np.mean(np.abs(signal)) + 1e-9)

    if crest < 2.0:
        return ultra_soft(signal)
    if crest < 3.0:
        return human_friendly(signal)
    return smooth_audio(signal)


# -----------------------------
# load_wav z obsługą błędów
# -----------------------------
def load_wav(path):
    try:
        sr, data = wavfile.read(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except ValueError:
        raise ValueError(f"Invalid or corrupted WAV file: {path}")

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
# process_file z dry/wet
# -----------------------------
def process_file(input_path, output_path, mode="auto", dry_wet=1.0):
    sr, data = load_wav(input_path)

    if mode == "auto":
        wet = auto_for_humans(data)
    elif mode == "soften_peaks":
        wet = soften_peaks(data)
    elif mode == "human_friendly":
        wet = human_friendly(data)
    elif mode == "ultra_soft":
        wet = ultra_soft(data)
    elif mode == "speech_clarity":
        wet = speech_clarity(data)
    elif mode == "smooth":
        wet = smooth_audio(data)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    # miksowanie oryginału i efektu
    out = (1.0 - dry_wet) * data + dry_wet * wet

    save_wav(output_path, sr, out)
    return out
