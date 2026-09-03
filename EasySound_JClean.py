import atexit
import os
import subprocess
import tempfile
import traceback

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
from tkinter import (
    Tk, Button, Scale, HORIZONTAL, Label, filedialog,
    Frame, LEFT, StringVar, Radiobutton,
)
import sounddevice as sd

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.easysound import (
    j_clean, apply_gain_and_soften,
    auto_for_humans, soften_peaks, human_friendly, ultra_soft,
    speech_clarity, smooth_audio,
)

# Tryby biblioteki (te same, co `process_file(mode=...)`) — WZAJEMNIE
# WYKLUCZAJĄCE SIĘ, nie da się ich sensownie łączyć checkboxami: to
# alternatywne ustawienia tej samej operacji wygładzania (np.
# `human_friendly` to już gotowe złożenie `smooth_audio`+`soften_peaks`,
# `auto` samo wybiera jeden z pozostałych trybów na podstawie sygnału),
# więc w GUI są radiobuttonami (dokładnie jak `mode` w `process_file` —
# jeden string, jedna gałąź if/elif). Naturalnie łączą się za to ze
# WSZYSTKIMI pozostałymi, już niezależnymi kontrolkami w oknie (filtr
# Butterwortha, wzmocnienie/redukcja pików, J-Clean) — te stosują się po
# kolei jedna na drugiej, tak jak dotychczas.
LIBRARY_MODES = {
    "Brak": None,
    "auto": auto_for_humans,
    "soften_peaks": soften_peaks,
    "human_friendly": human_friendly,
    "ultra_soft": ultra_soft,
    "speech_clarity": speech_clarity,
    "smooth": smooth_audio,
}

# ---------------------------------------
# GLOBALNE
# ---------------------------------------

PREVIEW_SECONDS = 10  # dlugosc fragmentu do Live Preview / wykresu przed-po

file_path = None
preview_original = None   # niezmieniony fragment (PREVIEW_SECONDS) — "przed"
preview_data = None       # roboczy fragment — modyfikowany np. przez J-Clean, "po"
preview_fs = None

_temp_files = []  # pliki tymczasowe (konwersje ffmpeg) do posprzatania


def _cleanup_temp_files():
    for path in _temp_files:
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass


atexit.register(_cleanup_temp_files)

# ---------------------------------------
# KONWERSJA
# ---------------------------------------

def convert_to_wav(path):
    """Konwertuje dowolny format do WAV przez ffmpeg, do unikalnego pliku
    tymczasowego (zamiast stałej nazwy `temp_input.wav`, żeby nie kolidować
    między kolejnymi konwersjami / plikami wciąż odtwarzanymi).

    Rzuca RuntimeError z czytelnym komunikatem, jeśli ffmpeg nie jest
    zainstalowany albo konwersja się nie powiedzie — zamiast pozwolić,
    żeby program dalej próbował wczytać nieistniejący/pusty plik i wywalił
    się nieczytelnym tracebackiem.
    """
    fd, temp = tempfile.mkstemp(suffix=".wav", prefix="easysound_")
    os.close(fd)
    _temp_files.append(temp)

    cmd = ["ffmpeg", "-y", "-i", path, temp]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise RuntimeError(
            "Nie znaleziono \"ffmpeg\" w PATH. Zainstaluj ffmpeg, aby "
            "wczytywać pliki inne niż WAV (MP3, M4A, FLAC, OGG)."
        )

    if result.returncode != 0 or not os.path.exists(temp) or os.path.getsize(temp) == 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        detail = stderr[-500:] if stderr else "brak szczegółów z ffmpeg."
        raise RuntimeError(f"Konwersja ffmpeg nie powiodła się:\n{detail}")

    return temp


def load_wav(path):
    fs, data = wavfile.read(path)
    data = data.astype(np.float32)
    if data.ndim > 1:
        data = data.mean(axis=1)
    return fs, data


def load_audio_for_gui(path):
    """Wczytuje dowolny plik audio (WAV wprost, inne formaty przez ffmpeg).

    Zwraca (fs, data) albo rzuca RuntimeError z komunikatem czytelnym dla
    użytkownika — GUI łapie ten wyjątek i pokazuje go w `status_label`
    zamiast pozwolić nieobsłużonemu błędowi wywalić całe okno.
    """
    if path.lower().endswith(".wav"):
        wav_path = path
        is_temp = False
    else:
        wav_path = convert_to_wav(path)
        is_temp = True

    try:
        fs, data = load_wav(wav_path)
    except Exception as e:
        raise RuntimeError(f"Nie udało się odczytać pliku audio:\n{e}")
    finally:
        # dane już w pamięci — plik tymczasowy po konwersji nie jest
        # dłużej potrzebny, sprzątamy go od razu zamiast czekać do wyjścia
        if is_temp and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
                _temp_files.remove(wav_path)
            except (OSError, ValueError):
                pass

    return fs, data

# ---------------------------------------
# FILTRY DSP
# ---------------------------------------

def lowpass(data, cutoff, fs):
    nyq = 0.5 * fs
    norm = cutoff / nyq
    b, a = butter(5, norm, btype='low')
    return lfilter(b, a, data)


def apply_library_mode(signal):
    """Stosuje wybrany tryb biblioteki (`mode_var`), jeśli inny niż "Brak".

    UWAGA SKALI: sygnał w tym pliku (od `load_wav` powyżej) jest w skali
    zbliżonej do int16 (nieznormalizowany do [-1, 1]), ale `soften_peaks`/
    `human_friendly`/`auto_for_humans` (gdy trafi w gałąź z pikami) mają
    twardo wpisane progi zakładające skalę [-1, 1] (np. threshold=0.85) —
    podanie im wartości rzędu tysięcy sprawiłoby, że każda próbka
    wygladałaby na "pik" i zostałaby ucięta. Dlatego normalizujemy do
    [-1, 1] przed wywołaniem trybu i skalujemy z powrotem po.
    """
    mode_fn = LIBRARY_MODES.get(mode_var.get())
    if mode_fn is None:
        return signal

    peak = np.max(np.abs(signal)) + 1e-9
    normalized = signal / peak
    try:
        processed = mode_fn(normalized)
    except Exception as e:
        traceback.print_exc()
        status_label.config(text=f"Błąd trybu '{mode_var.get()}': {e}")
        return signal
    return processed * peak


# ---------------------------------------
# WAVEFORM — "przed" i "po" na wspólnym wykresie (dwa podwykresy,
# wspólna oś czasu i wspólna skala amplitudy, żeby były bezpośrednio
# porównywalne)
# ---------------------------------------

def update_waveform_plot(after=None):
    if preview_original is None:
        return

    n = min(len(preview_original), preview_fs)
    if n == 0:
        return

    x = np.arange(n) / preview_fs
    before = preview_original[:n]
    after_slice = after[:n] if after is not None else None

    if after_slice is not None:
        y_max = max(np.max(np.abs(before)), np.max(np.abs(after_slice))) * 1.05 + 1e-9
    else:
        y_max = np.max(np.abs(before)) * 1.05 + 1e-9

    fig.clear()

    ax1 = fig.add_subplot(211)
    ax1.plot(x, before, color="orange", linewidth=0.8)
    ax1.set_ylabel("przed")
    ax1.set_ylim(-y_max, y_max)
    ax1.set_xlim(0, x[-1] if len(x) > 1 else 1.0)
    ax1.grid(True, which="both", linestyle="--", linewidth=0.3, alpha=0.6)
    ax1.set_title("Waveform: przed / po wygładzeniu")
    ax1.tick_params(labelbottom=False)

    ax2 = fig.add_subplot(212, sharex=ax1)
    if after_slice is not None:
        ax2.plot(x, after_slice, color="cyan", linewidth=0.8)
    ax2.set_ylabel("po")
    ax2.set_ylim(-y_max, y_max)
    ax2.set_xlabel("czas [s]")
    ax2.grid(True, which="both", linestyle="--", linewidth=0.3, alpha=0.6)

    fig.tight_layout()
    canvas.draw()

# ---------------------------------------
# ODSŁUCH
# ---------------------------------------

def play_preview():
    global preview_data, preview_fs
    if preview_data is None:
        return

    cutoff = cutoff_slider.get()
    gain = gain_slider.get() / 100.0
    soften = soften_slider.get() / 100.0

    moded = apply_library_mode(preview_data)
    filtered = lowpass(moded, cutoff, preview_fs)
    audio_int16 = apply_gain_and_soften(filtered, gain, soften)

    sd.play(audio_int16, preview_fs)
    update_waveform_plot(after=audio_int16)


def stop_preview():
    sd.stop()

# ---------------------------------------
# J‑CLEAN — PRZYCISK
# ---------------------------------------

def apply_jclean():
    global preview_data, preview_fs
    if preview_data is None:
        return

    cleaned = j_clean(preview_data)
    preview_data[:] = cleaned

    update_waveform_plot(after=preview_data)
    cleaned_int16 = np.clip(cleaned, -32767, 32767).astype(np.int16)
    sd.play(cleaned_int16, preview_fs)

# ---------------------------------------
# WYBÓR PLIKU
# ---------------------------------------

def choose_file():
    global file_path, preview_original, preview_data, preview_fs
    chosen = filedialog.askopenfilename(
        filetypes=[("Audio files", "*.*")]
    )
    if not chosen:
        return

    status_label.config(text=f"Wczytuję: {chosen}...")
    root.update_idletasks()

    try:
        fs, data = load_audio_for_gui(chosen)
    except RuntimeError as e:
        traceback.print_exc()
        status_label.config(text=f"Błąd wczytywania: {e}")
        return
    except Exception as e:
        traceback.print_exc()
        status_label.config(text=f"Nieoczekiwany błąd wczytywania: {e}")
        return

    file_path = chosen
    preview_fs = fs
    # dwie niezależne kopie: preview_original nigdy nie jest modyfikowany
    # (to jest "przed"), preview_data jest roboczą kopią, którą J-Clean
    # nadpisuje w miejscu ("po")
    n_preview = fs * PREVIEW_SECONDS
    preview_original = data[:n_preview].copy()
    preview_data = data[:n_preview].copy()
    status_label.config(text=f"Wybrano: {file_path}")
    update_waveform_plot()

# ---------------------------------------
# PRZETWARZANIE CAŁEGO PLIKU
# ---------------------------------------

def process_audio():
    global file_path
    if not file_path:
        status_label.config(text="Nie wybrano pliku!")
        return

    status_label.config(text="Przetwarzam...")
    root.update_idletasks()

    try:
        fs, data = load_audio_for_gui(file_path)
    except RuntimeError as e:
        traceback.print_exc()
        status_label.config(text=f"Błąd wczytywania: {e}")
        return
    except Exception as e:
        traceback.print_exc()
        status_label.config(text=f"Nieoczekiwany błąd wczytywania: {e}")
        return

    cutoff = cutoff_slider.get()
    gain = gain_slider.get() / 100.0
    soften = soften_slider.get() / 100.0

    try:
        moded = apply_library_mode(data)
        filtered = lowpass(moded, cutoff, fs)
        out_int16 = apply_gain_and_soften(filtered, gain, soften)
    except Exception as e:
        traceback.print_exc()
        status_label.config(text=f"Błąd przetwarzania: {e}")
        return

    save_path = filedialog.asksaveasfilename(
        defaultextension=".wav",
        filetypes=[("WAV files", "*.wav")],
        title="Zapisz wynik jako..."
    )
    if not save_path:
        return

    try:
        wavfile.write(save_path, fs, out_int16)
        status_label.config(text=f"Zapisano: {save_path}")
    except Exception as e:
        traceback.print_exc()
        status_label.config(text=f"Błąd zapisu: {e}")

# ---------------------------------------
# GUI
# ---------------------------------------

if __name__ == "__main__":
    root = Tk()
    root.title("EasySound LIVE + Waveform + J‑Clean")

    Button(root, text="Wybierz plik audio", command=choose_file).pack()

    Label(root, text="Tryb biblioteki (wygładzanie) — jeden naraz").pack()
    mode_var = StringVar(value="Brak")
    mode_frame = Frame(root)
    mode_frame.pack()
    for mode_name in LIBRARY_MODES:
        Radiobutton(
            mode_frame, text=mode_name, variable=mode_var, value=mode_name,
            command=lambda: play_preview(),
        ).pack(side=LEFT)

    Label(root, text="Częstotliwość odcięcia (Hz)").pack()
    cutoff_slider = Scale(root, from_=500, to=12000, orient=HORIZONTAL,
                          command=lambda x: play_preview())
    cutoff_slider.set(6000)
    cutoff_slider.pack()

    Label(root, text="Wzmocnienie (%)").pack()
    gain_slider = Scale(root, from_=50, to=200, orient=HORIZONTAL,
                        command=lambda x: play_preview())
    gain_slider.set(120)
    gain_slider.pack()

    Label(root, text="Redukcja pików (%)").pack()
    soften_slider = Scale(root, from_=50, to=100, orient=HORIZONTAL,
                          command=lambda x: play_preview())
    soften_slider.set(80)
    soften_slider.pack()

    Button(root, text="Oczyść strukturę (J‑Clean)", command=apply_jclean).pack()
    Button(root, text="Zatrzymaj odsłuch", command=stop_preview).pack()
    Button(root, text="Przetwórz cały plik", command=process_audio).pack()

    status_label = Label(root, text="Brak pliku")
    status_label.pack()

    fig = Figure(figsize=(9, 6), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    root.mainloop()
