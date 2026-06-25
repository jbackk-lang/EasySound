<p align="center">
  <img src="EasySound.png" width="220" alt="EasySound logo">
</p>

# EasySound — LIVE Preview + Waveform

Program do filtrowania i wygładzania dźwięku z podglądem na żywo oraz wizualizacją waveform.  
Obsługuje MP3, WAV, FLAC, OGG, M4A dzięki automatycznej konwersji przez ffmpeg.
EasySound powstał, żeby pomóc osobom wrażliwym słuchowo — wygładza ostre dźwięki i poprawia komfort słuchania.

---

## 🎧 Funkcje
- Live Preview (odsłuch 1 sekundy po każdej zmianie suwaka)
- Waveform (wykres fali w oknie programu)
- Filtr dolnoprzepustowy
- Wzmocnienie sygnału
- Redukcja ostrych pików
- Obsługa wielu formatów audio
- Zapis wyniku do WAV

---

## 🔧 Wymagania
- Python 3.10–3.14
- ffmpeg.exe w tym samym folderze co program
- Biblioteki:
  - numpy
  - scipy
  - simpleaudio
  - matplotlib

---

## 🚀 Instalacja
git clone https://github.com/jbackk-lang/EasySound.git (github.com in Bing)
cd EasySound
pip install -r requirements.txt


---

## ▶️ Uruchomienie
python livepreviewMP3_wave.py

---

## 🖥️ Jak używać
1. Kliknij **Wybierz plik audio**  
2. Waveform pojawi się automatycznie  
3. Ruszaj suwakami — usłyszysz efekt na żywo  
4. Kliknij **Przetwórz cały plik**, aby zapisać wynik jako WAV  

---

## 🧠 Jak działa EasySound
EasySound wygładza dźwięk, redukuje ostre elementy i poprawia komfort słuchania.  
Stosowane techniki:
- filtr dolnoprzepustowy (butterworth)
- wygładzanie oknem Hanninga
- redukcja pików (threshold + scaling)
- automatyczna konwersja MP3 → WAV

---

## 🎚 Tryby przetwarzania (biblioteka)
| Tryb | Opis |
|------|------|
| human | miękkie wygładzenie |
| ultra | maksymalne wygładzenie |
| speech | poprawa zrozumiałości mowy |
| auto | automatyczne wykrywanie ostrości |
| smooth_audio | surowe wygładzenie |
| soften_peaks | redukcja pików |

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
process_file("wyklad.wav", "wyklad_clarity.wav", mode="speech")

---

## 📦 Pipeline WAV
signal, rate = load_wav("input.wav")
processed = human_friendly(signal)
save_wav("output.wav", processed, rate)

---

## ✔️ Status projektu
- LIVE PREVIEW — działa
- Waveform — działa
- 6 trybów przetwarzania — działa
- pipeline WAV — kompletny
- brak błędów importu

---
▶️ Jak używać (CLI)
Kod
from auto_compress_test import auto_compress_test

print(auto_compress_test("test.wav"))
Wynik:

„Plik jest IDENTYCZNY po kompresji/dekompresji.”

„Plik został ZMIENIONY przez kompresję.”

---
## 📄 Licencja
MIT
