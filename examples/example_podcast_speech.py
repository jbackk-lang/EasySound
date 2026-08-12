"""Zastosowanie: podcasty, wyklady, nagrania mowy.

speech_clarity wygladza tlo (okno 21, odciecie -3dB ok. 1.6 kHz), ale
zachowuje 65% oryginalnych transjentow, zeby nie "zjadac" spolglosek
i utrzymac zrozumialosc mowy — w przeciwienstwie do ultra_soft, ktory
tlumi niemal wszystko powyzej ~265 Hz.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from easysound import process_file

if __name__ == "__main__":
    in_path = os.path.join(os.path.dirname(__file__), "sample_input.wav")
    out_path = os.path.join(os.path.dirname(__file__), "output_speech_clarity.wav")
    process_file(in_path, out_path, mode="speech_clarity")
    print(f"Zapisano (poprawa zrozumialosci mowy): {out_path}")
