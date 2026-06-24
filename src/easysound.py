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
