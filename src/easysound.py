import numpy as np

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
