"""Zastosowanie: nadwrazliwosc sluchowa (hiperakuzja, ASD, ADHD).

Tryb ultra_soft mocno wygladza sygnal (mierzone odciecie -3dB ok. 265 Hz
przy 44100 Hz — patrz README/testy), usuwajac wiekszosc ostrych,
wysokoczestotliwosciowych elementow, ktore czesto sa nieprzyjemne dla
osob nadwrazliwych na dzwiek. To NIE jest narzedzie medyczne.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from easysound import process_file

if __name__ == "__main__":
    in_path = os.path.join(os.path.dirname(__file__), "sample_input.wav")
    out_path = os.path.join(os.path.dirname(__file__), "output_ultra_soft.wav")
    process_file(in_path, out_path, mode="ultra_soft")
    print(f"Zapisano (maksymalne wygladzenie): {out_path}")
