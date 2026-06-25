import numpy as np
import subprocess
from scipy.io import wavfile
from scipy.signal import butter, lfilter
from tkinter import Tk, Button, Scale, HORIZONTAL, Label, filedialog
import simpleaudio as sa

file_path = None
preview_data = None
preview_fs = None

def convert_to_wav(path):
    temp = "temp_input.wav"
    cmd = ["ffmpeg", "-y", "-i", path, temp]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return temp

def load_wav(path):
    fs, data = wavfile.read(path)
    return fs, data.astype(np.float32)

def lowpass(data, cutoff, fs):
    nyq = 0.5 * fs
    norm = cutoff / nyq
    b, a = butter(5, norm, btype='low')
    return lfilter(b, a, data)

def play_preview():
    global preview_data, preview_fs
    if preview_data is None:
        return

    cutoff = cutoff_slider.get()
    gain = gain_slider.get() / 100.0
    soften = soften_slider.get() / 100.0

    filtered = lowpass(preview_data, cutoff, preview_fs)
    filtered *= gain

    max_val = np.max(np.abs(filtered))
    limit = max_val * soften
    filtered = np.clip(filtered, -limit, limit)

    audio = filtered.astype(np.int16).tobytes()
    sa.play_buffer(audio, 1, 2, preview_fs)

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
    filtered *= gain

    max_val = np.max(np.abs(filtered))
    limit = max_val * soften
    filtered = np.clip(filtered, -limit, limit)

    save_path = filedialog.asksaveasfilename(
        defaultextension=".wav",
        filetypes=[("WAV files", "*.wav")],
        title="Zapisz wynik jako..."
    )

    if save_path:
        wavfile.write(save_path, fs, filtered.astype(np.int16))
        status_label.config(text=f"Zapisano: {save_path}")

# ---------------- GUI ----------------

root = Tk()
root.title("EasySound LIVE Preview")

Button(root, text="Wybierz plik audio", command=choose_file).pack()

Label(root, text="Częstotliwość odcięcia (Hz)").pack()
cutoff_slider = Scale(root, from_=500, to=12000, orient=HORIZONTAL, command=lambda x: play_preview())
cutoff_slider.set(6000)
cutoff_slider.pack()

Label(root, text="Wzmocnienie (%)").pack()
gain_slider = Scale(root, from_=50, to=200, orient=HORIZONTAL, command=lambda x: play_preview())
gain_slider.set(120)
gain_slider.pack()

Label(root, text="Redukcja pików (%)").pack()
soften_slider = Scale(root, from_=50, to=100, orient=HORIZONTAL, command=lambda x: play_preview())
soften_slider.set(80)
soften_slider.pack()

Button(root, text="Przetwórz cały plik", command=process_audio).pack()

status_label = Label(root, text="Brak pliku")
status_label.pack()

root.mainloop()
