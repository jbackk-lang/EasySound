import numpy as np
from scipy.io import wavfile
from scipy.signal import convolve
from scipy.signal.windows import hann


# -----------------------------
# Walidacja wejścia
# -----------------------------
def _validate_signal(signal):
    if signal is None:
        raise ValueError("Signal is None.")
    signal = np.asarray(signal, dtype=float)
    if signal.ndim != 1:
        raise ValueError("Signal must be 1‑D array.")
    if signal.size == 0:
        raise ValueError("Signal must not be empty.")
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


# -----------------------------
# j_clean — topologiczne czyszczenie struktury (z EasySound_JClean.py)
# -----------------------------
def j_clean(signal):
    signal = _validate_signal(signal)
    n = len(signal)

    if n < 3:
        # zbyt krotki sygnal, zeby sensownie filtrowac
        return signal.copy()

    # dlugosc okna Hanninga MUSI byc nieparzysta i <= n, inaczej
    # np.convolve(..., mode="same") zwraca dluzszy wynik niz `signal`
    # (numpy definiuje "same" jako dlugosc max(len(a), len(v))), co
    # powodowalo blad ksztaltu przy krotkich sygnalach (np. n=220).
    if n >= 513:
        win_len = 513
    else:
        win_len = n if n % 2 == 1 else n - 1
    win_len = max(3, win_len)

    window = np.hanning(win_len)
    smooth = np.convolve(signal, window / window.sum(), mode="same")

    ksize = min(64, max(1, n // 4))
    kernel = np.ones(ksize) / ksize
    denoise = np.convolve(smooth, kernel, mode="same")

    cleaned = 0.7 * denoise + 0.3 * signal
    return cleaned


# -----------------------------
# TIMDRAnalyzer — eksperymentalna analiza fazowa (Λ = τ/ρ + J)
#
# UWAGA UCZCIWOSCI: to eksperymentalny wskaznik oparty na chwilowej fazie
# sygnalu analitycznego (transformata Hilberta), bez ustalonej walidacji
# psychoakustycznej ani klinicznej. Lambda rosnie, gdy faza sygnalu
# zmienia sie szybko i nierownomiernie (sygnal "poszarpany"/zaszumiony),
# a maleje dla sygnalow gladkich (czyste tony, wolno zmieniajace sie fale).
# Traktuj to jako pomocniczy wskaznik porownawczy (np. przed/po czyszczeniu),
# a nie jako bezwzgledna miare jakosci dzwieku.
# -----------------------------
class TIMDRAnalyzer:
    def __init__(self, signal=None, path=None, rate=None):
        if path is not None:
            rate, signal = load_wav(path)
        if signal is None:
            raise ValueError("Provide either `signal` or `path`.")

        signal = _validate_signal(signal)
        self.rate = rate
        self.data = signal
        norm_factor = np.max(np.abs(signal)) + 1e-9
        self.norm = signal / norm_factor

    # tau — operator skretu (lokalna zmiana fazy)
    def tau(self):
        from scipy.signal import hilbert
        analytic = hilbert(self.norm)
        phase = np.unwrap(np.angle(analytic))
        return np.gradient(phase)

    # rho — defekt (lokalna nierownosc sygnalu)
    def rho(self):
        r = np.abs(np.gradient(self.norm))
        r[r == 0] = 1e-9
        return r

    # J — kompresja informacyjna (lokalna redukcja)
    def J(self, tau):
        return np.gradient(tau)

    # Lambda — zlozony wskaznik "szorstkosci fazowej" sygnalu
    def Lambda(self):
        tau = self.tau()
        rho = self.rho()
        j = self.J(tau)
        return (tau / rho) + j

    def summary(self):
        """Zwraca statystyki Lambda.

        UWAGA: `rho` (mianownik) moze byc bliskie zeru dla lokalnie
        plaskich fragmentow sygnalu, co powoduje rzadkie, ale bardzo
        duze wartosci odstajace w Lambda (zaobserwowane w testach: max
        rzedu 1e5-1e8 dla realistycznych sygnalow). `mean`/`std`/`max`/
        `min` sa wiec silnie podatne na te odstajace wartosci. `median`
        jest znacznie stabilniejsza i zalecana do porownan przed/po."""
        L = self.Lambda()
        return {
            "mean": float(np.mean(L)),
            "median": float(np.median(L)),
            "std": float(np.std(L)),
            "max": float(np.max(L)),
            "min": float(np.min(L)),
        }

# -----------------------------
# apply_gain_and_soften — uzywane przez EasySound_JClean.py (GUI)
#
# POPRAWKA: oryginalna wersja w EasySound_JClean.py przycinala tylko do
# `max_val * soften` (gdzie max_val to JUZ wzmocniona amplituda po gain),
# a potem rzutowala wprost na int16 bez ograniczenia do zakresu
# [-32767, 32767]. Przy gain > 100% (suwak pozwala do 200%) wartosci
# przekraczaly zakres int16 i "zawijaly sie" (integer overflow) zamiast
# zostac uciete, dajac gwaltowne trzaski. Zweryfikowane numerycznie:
# dla gain=2.0, soften=1.0 probka o wartosci 33739.8 dawala po prostym
# rzutowaniu -31797 zamiast oczekiwanego, uciete +32767.
# -----------------------------
def apply_gain_and_soften(data, gain=1.0, soften=1.0):
    data = _validate_signal(data)
    filtered = data * gain
    max_val = np.max(np.abs(filtered)) + 1e-9
    limit = max_val * soften
    filtered = np.clip(filtered, -limit, limit)
    filtered = np.clip(filtered, -32767, 32767)
    return filtered.astype(np.int16)

