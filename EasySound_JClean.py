import numpy as np
import subprocess
from scipy.io import wavfile
from scipy.signal import butter, lfilter
from tkinter import Tk, Button, Scale, HORIZONTAL, Label, filedialog
import sounddevice as sd

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.easysound import j_clean, apply_gain_and_soften

# ---------------------------------------
# GLOBALNE
# ---------------------------------------

file_path = None
preview_data = None
preview_fs = None

# ---------------------------------------
# KONWERSJA
# ---------------------------------------

def convert_to_wav(path):
    temp = "temp_input.wav"
    cmd = ["ffmpeg", "-y", "-i", path, temp]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return temp

def load_wav(path):
    fs, data = wavfile.read(path)
    data = data.astype(np.float32)
    if data.ndim > 1:
        data = data.mean(axis=1)
    return fs, data

# ---------------------------------------
# FILTRY DSP
# ---------------------------------------

def lowpass(data, cutoff, fs):
    nyq = 0.5 * fs
    norm = cutoff / nyq
    b, a = butter(5, norm, btype='low')
    return lfilter(b, a, data)


# ---------------------------------------
# WAVEFORM
# ---------------------------------------

def update_waveform_plot():
    if preview_data is None:
        return

    fig.clear()
    ax = fig.add_subplot(111)

    n = min(len(preview_data), preview_fs)
    x = np.arange(n) / preview_fs

    ax.plot(x, preview_data[:n], color="cyan", linewidth=0.8)

    ax.set_xlabel("czas [s]")
    ax.set_ylabel("amplituda")
    ax.set_title("Waveform (preview)")

    ax.grid(True, which="both", linestyle="--", linewidth=0.3, alpha=0.6)
    ax.set_xlim(0, max(x) if max(x) < 1 else 1.0)

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

    filtered = lowpass(preview_data, cutoff, preview_fs)
    audio_int16 = apply_gain_and_soften(filtered, gain, soften)

    sd.play(audio_int16, preview_fs)

# ---------------------------------------
# J‑CLEAN — PRZYCISK
# ---------------------------------------

def apply_jclean():
    global preview_data, preview_fs
    if preview_data is None:
        return

    cleaned = j_clean(preview_data)
    preview_data[:] = cleaned

    update_waveform_plot()
    cleaned_int16 = np.clip(cleaned, -32767, 32767).astype(np.int16)
    sd.play(cleaned_int16, preview_fs)

# ---------------------------------------
# WYBÓR PLIKU
# ---------------------------------------

def choose_file():
    global file_path, preview_data, preview_fs
    file_path = filedialog.askopenfilename(
        filetypes=[("Audio files", "*.*")]
    )
    if not file_path:
        return

    if file_path.lower().endswith(".wav"):
        wav_path = file_path
    else:
        wav_path = convert_to_wav(file_path)

    fs, data = load_wav(wav_path)

    preview_fs = fs
    preview_data = data[:fs]  # 1 sekunda
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

    if file_path.lower().endswith(".wav"):
        wav_path = file_path
    else:
        wav_path = convert_to_wav(file_path)

    fs, data = load_wav(wav_path)

    cutoff = cutoff_slider.get()
    gain = gain_slider.get() / 100.0
    soften = soften_slider.get() / 100.0

    filtered = lowpass(data, cutoff, fs)
    out_int16 = apply_gain_and_soften(filtered, gain, soften)

    save_path = filedialog.asksaveasfilename(
        defaultextension=".wav",
        filetypes=[("WAV files", "*.wav")],
        title="Zapisz wynik jako..."
    )

    if save_path:
        wavfile.write(save_path, fs, out_int16)
        status_label.config(text=f"Zapisano: {save_path}")

# ---------------------------------------
# GUI
# ---------------------------------------

if __name__ == "__main__":
    root = Tk()
    root.title("EasySound LIVE + Waveform + J‑Clean")

    Button(root, text="Wybierz plik audio", command=choose_file).pack()

    Label(root, text="Częstotliwość odcięcia (Hz)").pack()
    cutoff_slider = Scale(root, from_=500, to=12000, orient=HORIZONTAL,
                          command=lambda x: (play_preview(), update_waveform_plot()))
    cutoff_slider.set(6000)
    cutoff_slider.pack()

    Label(root, text="Wzmocnienie (%)").pack()
    gain_slider = Scale(root, from_=50, to=200, orient=HORIZONTAL,
                        command=lambda x: (play_preview(), update_waveform_plot()))
    gain_slider.set(120)
    gain_slider.pack()

    Label(root, text="Redukcja pików (%)").pack()
    soften_slider = Scale(root, from_=50, to=100, orient=HORIZONTAL,
                          command=lambda x: (play_preview(), update_waveform_plot()))
    soften_slider.set(80)
    soften_slider.pack()

    Button(root, text="Oczyść strukturę (J‑Clean)", command=apply_jclean).pack()
    Button(root, text="Przetwórz cały plik", command=process_audio).pack()

    status_label = Label(root, text="Brak pliku")
    status_label.pack()

    fig = Figure(figsize=(5, 2), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack()

    root.mainloop()
