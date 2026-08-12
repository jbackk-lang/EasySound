"""Zastosowanie: TIMDRAnalyzer jako wskaznik "szorstkosci" sygnalu do
porownan przed/po czyszczeniu (np. w automatycznych testach QA).

UWAGA UCZCIWOSCI: to eksperymentalny wskaznik oparty na fazie sygnalu
analitycznego (Hilbert), bez ustalonej walidacji psychoakustycznej —
traktuj go jako wzgledny wskaznik porownawczy, nie bezwzgledna miare
"jakosci dzwieku". Patrz docstring klasy TIMDRAnalyzer w easysound.py.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from easysound import load_wav, ultra_soft, TIMDRAnalyzer

if __name__ == "__main__":
    in_path = os.path.join(os.path.dirname(__file__), "sample_input.wav")
    sr, data = load_wav(in_path)
    cleaned = ultra_soft(data)

    before = TIMDRAnalyzer(signal=data).summary()
    after = TIMDRAnalyzer(signal=cleaned).summary()

    print("Lambda (szorstkosc fazowa) przed czyszczeniem:", before)
    print("Lambda (szorstkosc fazowa) po czyszczeniu     :", after)
    # mean/std/max/min sa podatne na rzadkie, bardzo duze wartosci odstajace
    # (patrz docstring summary()) — median jest stabilniejsza do porownan
    print(f"median |Lambda| spadla o {(1 - abs(after['median']) / (abs(before['median']) + 1e-9)) * 100:.1f}%")
    print(f"std Lambda spadlo o {(1 - after['std'] / before['std']) * 100:.1f}%")
