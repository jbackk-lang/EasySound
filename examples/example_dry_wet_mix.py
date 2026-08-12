"""Zastosowanie: subtelne, czesciowe wygladzenie (dry/wet mix).

Zamiast stosowac efekt w 100%, mozna zmieszac go z oryginalem —
przydatne, gdy pelny tryb (np. ultra_soft) jest zbyt agresywny, ale
chcemy zachowac czesc jego dzialania.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from easysound import process_file

if __name__ == "__main__":
    in_path = os.path.join(os.path.dirname(__file__), "sample_input.wav")

    for wet in (0.25, 0.5, 0.75, 1.0):
        out_path = os.path.join(os.path.dirname(__file__), f"output_dry_wet_{wet}.wav")
        process_file(in_path, out_path, mode="ultra_soft", dry_wet=wet)
        print(f"dry_wet={wet} -> {out_path}")
