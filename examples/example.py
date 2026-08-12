"""Najprostszy przyklad: pelny pipeline plik-do-pliku w trybie automatycznym."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from easysound import process_file

if __name__ == "__main__":
    in_path = os.path.join(os.path.dirname(__file__), "sample_input.wav")
    out_path = os.path.join(os.path.dirname(__file__), "output_auto.wav")
    process_file(in_path, out_path)
    print(f"Zapisano: {out_path}")
