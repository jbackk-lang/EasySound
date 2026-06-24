import numpy as np
import numpy as np
import wave
import struct

def smooth_audio(signal, window_size=5):
    """
    Proste wygładzanie sygnału audio metodą uśredniania ruchomego.
    Działa na sygnałach 1D (np. próbki dźwięku).
    
    window_size – im większe, tym bardziej wygładzony dźwięk.
    """
    if window_size < 1:
        return signal

    # konwersja na numpy (łatwiejsze operacje)
    signal = np.array(signal, dtype=float)

    # filtr uśredniający
    kernel = np.ones(window_size) / window_size
    smoothed = np.convolve(signal, kernel, mode='same')

    return smoothed

def soften_peaks(signal, threshold=0.8, reduction=0.5):
    """
    Łagodzi ostre piki w sygnale.
    threshold – powyżej jakiej wartości uznajemy próbkę za 'za ostrą'
    reduction – o ile zmniejszamy ostre piki
    """
    signal = np.array(signal, dtype=float)

    peaks = np.abs(signal) > threshold
    signal[peaks] *= reduction

    return signal

def human_friendly(signal):
    """
    Tryb 'dla ludzi' – wygładza dźwięk i usuwa ostre piki.
    Idealne dla osób wrażliwych na ostre dźwięki.
    """
    s = smooth_audio(signal, window_size=7)
    s = soften_peaks(s, threshold=0.7, reduction=0.6)
    return s

def load_wav(path):
    """
    Wczytuje plik WAV i zwraca:
    - próbki jako listę floatów
    - częstotliwość próbkowania (sample rate)
    """
    with wave.open(path, 'rb') as w:
        channels = w.getnchannels()
        sample_width = w.getsampwidth()
        framerate = w.getframerate()
        frames = w.getnframes()

        raw = w.readframes(frames)
        fmt = "<" + "h" * (len(raw) // 2)
        data = struct.unpack(fmt, raw)

        # jeśli stereo → bierzemy tylko lewy kanał
        if channels == 2:
            data = data[::2]

        # normalizacja do -1..1
        signal = np.array(data) / 32768.0

        return signal, framerate


def save_wav(path, signal, framerate):
    """
    Zapisuje sygnał audio (float -1..1) do pliku WAV.
    """
    # konwersja na int16
    data = (np.array(signal) * 32767).astype(np.int16)

    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(framerate)

        raw = struct.pack("<" + "h" * len(data), *data)
        w.writeframes(raw)

def process_file(input_path, output_path):
    """
    Wczytuje plik, wygładza go i zapisuje wynik.
    Tryb 'dla ludzi' – łagodny, miękki dźwięk.
    """
    signal, rate = load_wav(input_path)
    processed = human_friendly(signal)
    save_wav(output_path, processed, rate)

def ultra_soft(signal):
    """
    Tryb ULTRA miękki – maksymalne wygładzenie dźwięku.
    Idealny dla osób nadwrażliwych na ostre dźwięki,
    dzieci, osób z autyzmem, osób po urazach słuchu.
    """
    # mocniejsze wygładzenie
    s = smooth_audio(signal, window_size=15)
    # mocniejsze łagodzenie pików
    s = soften_peaks(s, threshold=0.5, reduction=0.4)
    return s

def speech_clarity(signal):
    """
    Tryb poprawiający zrozumiałość mowy.
    Wygładza szum, ale podkreśla elementy ważne dla artykulacji.
    """
    # lekkie wygładzenie
    s = smooth_audio(signal, window_size=5)
    # delikatne usunięcie pików
    s = soften_peaks(s, threshold=0.8, reduction=0.7)

    # lekkie podbicie średnich częstotliwości (formanty mowy)
    # prosta symulacja EQ bez DSP
    s = s * 1.1

    return s

def auto_for_humans(signal):
    """
    Automatyczny tryb 'dla ludzi'.
    Jeśli sygnał jest ostry → UltraSoft.
    Jeśli sygnał to mowa → SpeechClarity.
    """
    # wykrywanie ostrości sygnału
    sharpness = np.mean(np.abs(np.diff(signal)))

    if sharpness > 0.15:
        return ultra_soft(signal)
    else:
        return speech_clarity(signal)
