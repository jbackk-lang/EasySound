"""Zastosowanie: odtwarzanie audio z automatycznym rozpoznawaniem formatu
(WAV/FLAC/OGG przez soundfile; MP3/M4A/AAC/... przez pydub+ffmpeg).

UWAGA: odtwarzanie dzwieku (`play_audio`) wymaga zainstalowanej biblioteki
PortAudio (backend `sounddevice`) oraz karty dzwiekowej / urzadzenia
audio — w srodowiskach headless/CI ten przyklad moze nie dzialac. Sama
funkcja dekodujaca (`decode_audio`) dziala zawsze, niezaleznie od
dostepnosci PortAudio, wiec ponizszy przyklad pokazuje oba kroki osobno.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from audio_playback import decode_audio, play_audio

if __name__ == "__main__":
    in_path = os.path.join(os.path.dirname(__file__), "sample_input.wav")
    if not os.path.exists(in_path):
        from _make_sample_audio import make_sample_wav
        make_sample_wav(in_path)

    # krok 1: dekodowanie (dziala zawsze, bez PortAudio)
    data, fs = decode_audio(in_path)
    print(f"Zdekodowano: {len(data)} probek, fs={fs}, "
          f"kanaly={'stereo' if data.ndim > 1 else 'mono'}")

    # krok 2: odtworzenie (wymaga PortAudio + urzadzenia audio)
    try:
        play_audio(in_path)
        print("Odtworzono.")
    except Exception as e:
        print(f"Nie udalo sie odtworzyc dzwieku (to normalne w srodowisku "
              f"bez karty dzwiekowej / PortAudio): {e}")
