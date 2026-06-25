<p align="center">
  <img src="EasySound.png" width="220" alt="EasySound logo">
</p>

# EasySound LIVE Preview

Program do filtrowania dźwięku z podglądem na żywo (LIVE PREVIEW).
Działa z plikami MP3, WAV, FLAC, OGG, M4A — dzięki automatycznej konwersji przez ffmpeg.

## Funkcje
- Podgląd efektu na żywo (1 sekunda audio)
- Filtr dolnoprzepustowy
- Wzmocnienie sygnału
- Redukcja pików
- Obsługa MP3/WAV/FLAC/M4A/OGG
- Zapis do WAV

## Wymagania
- Python 3.10–3.14
- ffmpeg.exe w tym samym folderze co program
- Biblioteki:
  - numpy
  - scipy
  - simpleaudio

## Uruchomienie
1. Pobierz lub sklonuj repozytorium:
git clone https://github.com/jbackk-lang/EasySound.git (github.com in Bing)
albo pobierz ZIP i rozpakuj.

2. Upewnij się, że w folderze z programem znajduje się `ffmpeg.exe`.
- Jeśli nie masz ffmpeg, pobierz stąd: https://www.gyan.dev/ffmpeg/builds/
- Skopiuj `ffmpeg.exe` do tego samego folderu co plik `.py`.

3. Zainstaluj wymagane biblioteki:

pip install -r requirements.txt
4. Uruchom program:
python livepreviewMP3.py

5. W oknie programu:
- kliknij **Wybierz plik audio**
- ruszaj suwakami, aby odsłuchać **LIVE PREVIEW**
- kliknij **Przetwórz cały plik**, aby zapisać wynik jako WAV

# EasySound

EasySound to prosta biblioteka audio, która wygładza dźwięk tak, aby był łatwiejszy do słuchania i rozumienia.  
Projekt powstał z myślą o osobach, które mają trudności z odbiorem mowy lub dźwięków o ostrych krawędziach.

## Funkcje (plan)
- wygładzanie przebiegu dźwięku
- usuwanie artefaktów (kliknięcia, trzaski)
- zachowanie naturalnej barwy i rezonansu
- filtracja przyjazna dla ucha

## Status
Wersja początkowa — struktura projektu.

# EasySound

EasySound to lekka biblioteka audio, która wygładza dźwięk tak, aby był łatwiejszy do słuchania i rozumienia.  
Projekt powstał z myślą o osobach wrażliwych na ostre dźwięki, dzieciach, osobach z autyzmem, osobach po urazach słuchu oraz wszystkich, którzy mają trudności z odbiorem mowy.

## Funkcje

EasySound oferuje kilka trybów przetwarzania:

### 🔹 smooth_audio
Podstawowe wygładzanie sygnału metodą uśredniania ruchomego.

### 🔹 soften_peaks
Łagodzenie ostrych pików (kliknięcia, trzaski, nagłe skoki).

### 🔹 human_friendly
Tryb „dla ludzi” – miękkie wygładzenie i redukcja ostrych elementów.

### 🔹 ultra_soft
Najłagodniejszy tryb – maksymalne wygładzenie dźwięku.  
Idealny dla osób nadwrażliwych na bodźce.

### 🔹 speech_clarity
Tryb poprawiający zrozumiałość mowy.  
Wygładza szum, ale podkreśla elementy ważne dla artykulacji.

### 🔹 auto_for_humans
Tryb automatyczny – sam wybiera najlepszą metodę w zależności od sygnału.

---

## Obsługa plików WAV

EasySound potrafi:

- wczytać plik WAV (`load_wav`)
- przetworzyć go dowolnym trybem
- zapisać wynik (`save_wav`)
- wykonać pełny pipeline (`process_file`)

---

## Przykład użycia

```python
from easysound import process_file

process_file("input.wav", "output.wav")

Cel projektu
EasySound ma pomagać ludziom:

słyszeć dźwięki w sposób bardziej komfortowy,

lepiej rozumieć mowę,

redukować stres wywołany ostrymi bodźcami,

poprawiać komunikację.

To narzędzie wspierające, nie medyczne.

EasySound
Biblioteka audio wspomagająca słuch — wygładzanie, łagodzenie pików, poprawa mowy.  
Python · WAV → WAV · 6 trybów przetwarzania

EasySound to lekka biblioteka do łagodzenia dźwięku dla osób wrażliwych słuchowo, z wadami słuchu, po urazach, z hiperakuzją, APD, autyzmem lub po prostu dla każdego, kto chce mieć „miększy”, przyjemniejszy dźwięk.
Działa na plikach WAV i oferuje 6 trybów psychoakustycznych.

✨ Funkcje
wygładzanie sygnału (okno Hanninga)

redukcja ostrych pików

poprawa zrozumiałości mowy

automatyczne wykrywanie kliknięć i impulsów

obsługa WAV (load → process → save)

6 trybów przetwarzania

🎧 Zastosowania (praktyczne)
✔ Niedosłuch wysokoczęstotliwościowy
Tryb: speech  
Poprawia zrozumiałość mowy, łagodzi sybilanty.

✔ Nadwrażliwość słuchowa (hiperakuzja, autyzm, ADHD)
Tryb: ultra  
Maksymalne wygładzenie, brak ostrych dźwięków.

✔ Rehabilitacja po urazach słuchu / szumy uszne
Tryb: human  
Łagodny, naturalny dźwięk bez nagłych skoków.

✔ Problemy z przetwarzaniem słuchowym (APD)
Tryb: speech  
Wzmacnia sygnał mowy, redukuje szum tła.

✔ Dzieci wrażliwe na dźwięki
Tryb: human  
Miękkie bajki, brak agresywnych sybilantów.

✔ Osoby starsze z aparatami słuchowymi
Tryb: auto  
Wykrywa kliknięcia i przełącza się na ultra_soft.

🧪 Przykłady użycia
1. Wygładzenie ostrego nagrania
python
from easysound import process_file
process_file("raw.wav", "soft.wav", mode="human")
2. Usuwanie kliknięć i trzasków
python
process_file("podcast.wav", "podcast_clean.wav", mode="auto")
3. Poprawa mowy (wykład, spotkanie)
python
process_file("wyklad.wav", "wyklad_clarity.wav", mode="speech")
4. Nagrania terenowe (wiatr, ruch uliczny)
python
process_file("field.wav", "field_soft.wav", mode="auto")
🎚 Tryby przetwarzania
Tryb	Opis
human	miękkie wygładzenie + redukcja ostrych elementów
ultra	maksymalne wygładzenie dla bardzo wrażliwych uszu
speech	poprawa zrozumiałości mowy, kontrola sybilantów
auto	automatyczne wykrywanie ostrości i kliknięć
smooth_audio	surowe wygładzenie oknem Hanninga
soften_peaks	redukcja pików powyżej progu


🔧 Pipeline WAV
python
signal, rate = load_wav("input.wav")
processed = human_friendly(signal)
save_wav("output.wav", processed, rate)
📦 Instalacja (lokalna)
bash
git clone https://github.com/jbackk-lang/EasySound
cd EasySound
python3 examples/example.py
🧠 Jak to działa (w skrócie)
wygładzanie: okno Hanninga + konwolucja

redukcja pików: threshold + scaling

auto: analiza pochodnej sygnału (średnia + maksymalny impuls)

speech: wygładzenie + kontrola sybilantów + bezpieczny clip

✔ Status
9 funkcji działa

6 trybów przetwarzania

pipeline WAV kompletny

testy przechodzą

brak błędów importu
