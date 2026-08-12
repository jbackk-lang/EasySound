"""Odtwarzanie audio z automatycznym dekodowaniem WAV/FLAC/OGG/MP3/M4A/AAC.

`decode_audio()` jest czysta funkcja (bez zaleznosci od sounddevice/karty
dzwiekowej) i mozna ja bezpiecznie testowac i importowac nawet w srodowisku
bez zainstalowanej biblioteki PortAudio. `play_audio()` importuje
`sounddevice` dopiero w momencie wywolania — dzieki temu reszta modulu
(w tym `decode_audio`) dziala nawet jesli PortAudio nie jest dostepne.
"""
import os

import numpy as np
import soundfile as sf
from pydub import AudioSegment

_SOUNDFILE_EXTS = {".wav", ".flac", ".ogg"}

# maksymalna wartosc calkowita dla danej liczby bajtow na probke (do
# normalizacji do zakresu [-1, 1], spojnego z reszta EasySound)
_MAX_INT_FOR_WIDTH = {
    1: 2 ** 7,
    2: 2 ** 15,
    3: 2 ** 23,
    4: 2 ** 31,
}


def _decode_with_pydub(path):
    audio = AudioSegment.from_file(path)

    samples = np.array(audio.get_array_of_samples(), dtype=np.float64)

    max_val = _MAX_INT_FOR_WIDTH.get(audio.sample_width)
    if max_val is None:
        raise ValueError(
            f"Nieobslugiwana szerokosc probki: {audio.sample_width} bajtow "
            f"(plik: {path})"
        )
    samples /= max_val

    if audio.channels > 1:
        samples = samples.reshape((-1, audio.channels))

    return samples, audio.frame_rate


def decode_audio(path):
    """Wczytuje plik audio i zwraca (data, samplerate).

    `data` jest znormalizowane do zakresu [-1, 1] (float), mono jako
    tablica 1-D, wielokanalowe jako (n_probek, n_kanalow) — niezaleznie
    od formatu wejsciowego i szerokosci probki zrodlowej.

    WAV/FLAC/OGG sa dekodowane przez `soundfile` (bez zewnetrznych
    zaleznosci binarnych). Pozostale formaty (MP3, M4A, AAC, ...) sa
    dekodowane przez `pydub`, co wymaga zainstalowanego `ffmpeg` w PATH.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()

    if ext in _SOUNDFILE_EXTS:
        try:
            data, fs = sf.read(path)
        except Exception as e:
            raise ValueError(f"Invalid or corrupted audio file: {path} ({e})")
        return data, fs

    try:
        return _decode_with_pydub(path)
    except FileNotFoundError:
        raise
    except Exception as e:
        raise ValueError(
            f"Could not decode audio file: {path} ({e}). "
            f"Upewnij sie, ze ffmpeg jest zainstalowany i dostepny w PATH."
        )


def play_audio(filename: str, blocking: bool = True):
    """Odtwarza plik audio (WAV/FLAC/OGG/MP3/M4A/AAC/...).

    Wymaga zainstalowanej biblioteki PortAudio (uzywanej przez
    `sounddevice`) oraz — dla formatow innych niz WAV/FLAC/OGG —
    zewnetrznego `ffmpeg` w PATH (uzywanego przez `pydub`).
    """
    import sounddevice as sd  # import lazy: dzialanie decode_audio() nie
                               # powinno zalezec od obecnosci PortAudio

    data, fs = decode_audio(filename)
    sd.play(data, fs)
    if blocking:
        sd.wait()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uzycie: python audio_playback.py plik.mp3")
        sys.exit(1)
    play_audio(sys.argv[1])
