<p align="center">
  <img src="EasySound.png" width="220" alt="EasySound logo">
</p>

# EasySound — LIVE Preview + Waveform + J‑Clean
Program do filtrowania, wygładzania i czyszczenia struktury dźwięku z podglądem na żywo oraz wizualizacją waveform.
Obsługuje MP3, WAV, FLAC, OGG, M4A dzięki automatycznej konwersji przez ffmpeg.

EasySound powstał, żeby pomóc osobom wrażliwym słuchowo — wygładza ostre dźwięki, redukuje szum informacyjny
i poprawia komfort słuchania.

---

## 🎧 Funkcje

- **Live Preview** — odsłuch 1 sekundy po każdej zmianie suwaka   
- **Waveform** — wykres fali w oknie programu  
- **Filtr dolnoprzepustowy** (Butterworth)  
- **Wzmocnienie sygnału**  
- **Redukcja ostrych pików**  
- **J‑Clean (topologiczne czyszczenie struktury)** — wygładza skręt, usuwa szum informacyjny i przywraca czystą falę  
- Obsługa wielu formatów audio  
- Zapis wyniku do WAV  

---

## 🔧 Wymagania

- Python 3.10–3.14  
- `ffmpeg.exe` w tym samym folderze co program  
- Biblioteki:
  - numpy
  - scipy
  - simpleaudio
  - matplotlib

---

## 🚀 Instalacja
git clone https://github.com/jbackk-lang/EasySound.git
cd EasySound
pip install -r requirements.txt


---

## ▶️ Uruchomienie
python EasySound_JClean.py

---

## 🖥️ Jak używać

1. Kliknij **Wybierz plik audio**  
2. Waveform pojawi się automatycznie  
3. Ruszaj suwakami — usłyszysz efekt na żywo  
4. Kliknij **Oczyść strukturę (J‑Clean)**, aby odszumić i wygładzić falę  
5. Kliknij **Przetwórz cały plik**, aby zapisać wynik jako WAV  

---

## 🧠 Jak działa EasySound

EasySound wygładza dźwięk, redukuje ostre elementy i poprawia komfort słuchania .  
Stosowane techniki:

- filtr dolnoprzepustowy (Butterworth)  
- wygładzanie oknem Hanninga  
- redukcja pików (threshold + scaling)  
- automatyczna konwersja MP3 → WAV  
- **J‑Clean** — topologiczne czyszczenie struktury sygnału (model J)

---

## 🎚 Tryby przetwarzania (biblioteka)

| Tryb          | Opis |
|---------------|------|
| human         | miękkie wygładzenie |
| ultra         | maksymalne wygładzenie |
| speech        | poprawa zrozumiałości mowy |
| auto          | automatyczne wykrywanie ostrości |
| smooth_audio  | surowe wygładzenie |
| soften_peaks  | redukcja pików |
| **j_clean**   | czyszczenie struktury sygnału |

---

## 🎧 Zastosowania

- nadwrażliwość słuchowa (autyzm, ADHD, hiperakuzja)  
- poprawa mowy (wykłady, podcasty)  
- redukcja kliknięć i trzasków  
- łagodzenie ostrych dźwięków  
- nagrania terenowe  
- osoby starsze z aparatami słuchowymi  

---

## 🧪 Przykłady użycia (biblioteka)
from easysound import process_file
process_file("raw.wav", "soft.wav", mode="human")
process_file("podcast.wav", "podcast_clean.wav", mode="auto")
from easysound import j_clean
clean = j_clean(signal)

---

## 📦 Pipeline WAV
signal, rate = load_wav("input.wav")
processed = human_friendly(signal)
save_wav("output.wav", processed, rate)

---

## ✔️ Status projektu

- LIVE PREVIEW — działa  
- Waveform — działa  
- J‑Clean — działa  
- 6 trybów przetwarzania — działa  
- pipeline WAV — kompletny  
- brak błędów importu  

---
## Uzasadnienie DSP i psychoakustyczne

Każdy z 6 trybów został zaprojektowany na podstawie znanych efektów
psychoakustycznych:

- ultra_soft — redukcja energii powyżej 3.5 kHz zmniejsza pobudzenie
  układu słuchowego u osób z ASD (badania: hypersensitivity to high
  frequencies 3–8 kHz).
- speech_clarity — wzmocnienie 1–3 kHz poprawia zrozumiałość mowy
  (formant F2/F3), szczególnie przy niedosłuchu wysokotonowym.
- soften_peaks — limiter piku usuwa transjenty, które są głównym
  wyzwalaczem dyskomfortu u osób z hiperakuzją.
- human_friendly — redukcja centroidu widma poprawia percepcję mowy
  u dzieci i osób uczących się języka.
---
import numpy as np

import scipy.io.wavfile as wav

from scipy.signal import hilbert

class EasySound:
    def __init__(self, path):
        self.rate, self.data = wav.read(path)
        self.data = self.data.astype(np.float32)
        self.norm = self.data / np.max(np.abs(self.data))

    # τ — operator skrętu (lokalna zmiana fazy)
    def tau(self):
        analytic = hilbert(self.norm)
        phase = np.unwrap(np.angle(analytic))
        tau = np.gradient(phase)
        return tau

    # ρ — defekt (lokalna nierówność sygnału)
    def rho(self):
        rho = np.abs(np.gradient(self.norm))
        rho[rho == 0] = 1e-9
        return rho

    # J — kompresja informacyjna (lokalna redukcja)
    def J(self, tau):
        return np.gradient(tau)

    # Λ — transformacja (częściowy wzór)
    def Lambda(self):
        tau = self.tau()
        rho = self.rho()
        J = self.J(tau)
        Lambda = (tau / rho) + J
        return Lambda

    def summary(self):
        L = self.Lambda()
        return {
            "mean": float(np.mean(L)),
            "std": float(np.std(L)),
            "max": float(np.max(L)),
            "min": float(np.min(L))
        }

# przykład użycia
# es = EasySound("plik.wav")
# print(es.summary())
---
## 📄 Licencja

MIT

