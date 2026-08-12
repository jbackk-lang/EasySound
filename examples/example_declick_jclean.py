"""Zastosowanie: usuwanie klikniec/trzaskow z nagran terenowych lub starych
zrodel audio (winyl, tasmy) — funkcja j_clean.

j_clean laczy szerokie wygladzanie oknem Hanninga z dodatkowym filtrem
srednioruchomym, mieszajac wynik 70/30 z oryginalem, zeby stlumic ostre
piki bez calkowitego "wyplaszczenia" sygnalu.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from easysound import load_wav, save_wav, j_clean

if __name__ == "__main__":
    in_path = os.path.join(os.path.dirname(__file__), "sample_input.wav")
    out_path = os.path.join(os.path.dirname(__file__), "output_jclean.wav")

    sr, data = load_wav(in_path)
    cleaned = j_clean(data)

    print(f"Szczyt przed: {np.max(np.abs(data)):.3f}, po: {np.max(np.abs(cleaned)):.3f}")
    save_wav(out_path, sr, cleaned)
    print(f"Zapisano: {out_path}")
