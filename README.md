<p align="center">
  <img src="EasySound.png" width="220" alt="EasySound logo">
</p>


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
