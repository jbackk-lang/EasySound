"""Zastosowanie: przetwarzanie wsadowe wielu plikow (np. calego archiwum
nagran terenowych lub odcinkow podcastu) w trybie auto_for_humans, ktory
sam dobiera metode na podstawie charakterystyki kazdego sygnalu."""
import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from easysound import process_file

if __name__ == "__main__":
    in_dir = os.path.dirname(__file__)
    out_dir = os.path.join(in_dir, "batch_output")
    os.makedirs(out_dir, exist_ok=True)

    input_files = glob.glob(os.path.join(in_dir, "sample_input.wav"))
    for in_path in input_files:
        name = os.path.basename(in_path)
        out_path = os.path.join(out_dir, f"clean_{name}")
        process_file(in_path, out_path, mode="auto")
        print(f"{name} -> {out_path}")
