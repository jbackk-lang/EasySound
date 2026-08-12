<p align="center">
  <img src="EasySound.png" width="220" alt="EasySound logo">
</p>

# EasySound

EasySound to lekka biblioteka audio, która wygładza dźwięk, redukuje ostre piki
i poprawia zrozumiałość mowy. Do biblioteki dołączony jest opcjonalny program
GUI (`EasySound_JClean.py`) z podglądem na żywo i wizualizacją waveform.

Projekt powstał z myślą o osobach wrażliwych słuchowo (nadwrażliwość,
hiperakuzja, ASD, ADHD), osobach z ubytkiem słuchu oraz każdym, kto ma
trudności z odbiorem ostrych dźwięków lub niewyraźnej mowy.

**To narzędzie wspierające, nie medyczne.**

---

## 🎧 Funkcje

Biblioteka (`easysound.py`) udostępnia:

| Tryb | Co robi | Zmierzone odcięcie −3dB (przy 44100 Hz)* |
|---|---|---|
| `smooth_audio` | wygładzanie oknem Hanninga (okno domyślne 51) | ~635 Hz |
| `soften_peaks` | miękki limiter (soft-knee) na ostrych pikach | — (działa na amplitudzie, nie na częstotliwości) |
| `human_friendly` | `smooth_audio` (okno 41) + `soften_peaks` | ~793 Hz + limiter |
| `ultra_soft` | najmocniejsze wygładzenie (okno 121) | ~265 Hz |
| `speech_clarity` | wygładza tło (okno 21), ale zachowuje 65% transjentów | ~1586 Hz (tło); transjenty częściowo zachowane |
| `auto_for_humans` | automatycznie dobiera tryb na podstawie impulsowości i crest factora sygnału | — |
| `j_clean` | szerokie wygładzanie + dodatkowy filtr, mieszany 70/30 z oryginałem | ~85 Hz (okno 513) |
| `TIMDRAnalyzer` | eksperymentalny wskaźnik "szorstkości fazowej" sygnału (patrz niżej) | — |

\* Odcięcie −3dB jest **proporcjonalne do częstotliwości próbkowania** —
każdy z trybów opiera się na oknie o stałej liczbie próbek, więc przy innym
`fs` te wartości się przeskalują (np. przy 22050 Hz odcięcia będą o połowę
niższe). Wartości w tabeli zostały **zmierzone** (FFT odpowiedzi
częstotliwościowej okna), nie założone — test `test_measured_minus3db_cutoffs`
w `tests/test_easysound.py` pilnuje, żeby kod i ta tabela się nie rozjechały.

Program GUI (`EasySound_JClean.py`) dodatkowo oferuje:

- **Live Preview** — odsłuch 1 sekundy po każdej zmianie suwaka
- **Waveform** — wykres fali w oknie programu
- filtr dolnoprzepustowy Butterwortha (niezależny od trybów bibliotecznych)
- **J-Clean** — przycisk uruchamiający `j_clean` na podglądzie
- konwersję MP3/FLAC/OGG/M4A → WAV przez zewnętrzny `ffmpeg`

---

## 🔧 Wymagania

- Python 3.10+
- Biblioteki: `numpy`, `scipy`
- Do GUI dodatkowo: `simpleaudio`, `matplotlib`, oraz `ffmpeg` w PATH lub w
  folderze programu (tylko jeśli chcesz wczytywać pliki inne niż WAV)

```
pip install -r requirements.txt
```

---

## 🚀 Instalacja

```
git clone https://github.com/jbackk-lang/EasySound.git
cd EasySound
pip install -r requirements.txt
```

---

## ▶️ Użycie biblioteki

```python
from easysound import process_file

process_file("input.wav", "output.wav", mode="human_friendly")
```

Dostępne wartości `mode`: `"auto"`, `"soften_peaks"`, `"human_friendly"`,
`"ultra_soft"`, `"speech_clarity"`, `"smooth"`.

```python
from easysound import load_wav, save_wav, j_clean

sr, data = load_wav("input.wav")
cleaned = j_clean(data)
save_wav("output.wav", sr, cleaned)
```

Mieszanie oryginału z efektem (dry/wet):

```python
process_file("input.wav", "output.wav", mode="ultra_soft", dry_wet=0.5)
```

## 🖥️ Uruchomienie GUI

```
python EasySound_JClean.py
```

1. Kliknij **Wybierz plik audio**
2. Waveform pojawi się automatycznie
3. Ruszaj suwakami — usłyszysz efekt na żywo
4. Kliknij **Oczyść strukturę (J-Clean)**, żeby odszumić i wygładzić falę
5. Kliknij **Przetwórz cały plik**, żeby zapisać wynik jako WAV

---

## 🎧 Zastosowania

Każdy z poniższych przykładów to gotowy, uruchamialny skrypt w `examples/`
(generuje własny przykładowy plik WAV, więc działa od razu, bez potrzeby
dostarczania nagrania):

| Zastosowanie | Skrypt | Tryb |
|---|---|---|
| Nadwrażliwość słuchowa (hiperakuzja, ASD, ADHD) | `example_accessibility.py` | `ultra_soft` |
| Podcasty, wykłady, nagrania mowy | `example_podcast_speech.py` | `speech_clarity` |
| Usuwanie trzasków z nagrań terenowych / starych źródeł | `example_declick_jclean.py` | `j_clean` |
| Subtelne, częściowe wygładzenie (nie w 100%) | `example_dry_wet_mix.py` | `dry_wet` |
| Przetwarzanie wsadowe wielu plików | `example_batch_processing.py` | `auto` |
| Porównanie "szorstkości" sygnału przed/po (QA) | `example_timdr_analysis.py` | `TIMDRAnalyzer` |
| Minimalny przykład | `example.py` | `auto` |

Uruchomienie dowolnego przykładu:

```
cd examples
python example_accessibility.py
```

---

## 🧪 TIMDRAnalyzer — eksperymentalna analiza fazowa (Λ)

```python
from easysound import TIMDRAnalyzer

a = TIMDRAnalyzer(path="input.wav")
print(a.summary())
# {'mean': ..., 'median': ..., 'std': ..., 'max': ..., 'min': ...}
```

`TIMDRAnalyzer` liczy chwilową fazę sygnału (transformata Hilberta, `τ`),
jej lokalną zmienność (`ρ`) i lokalną zmianę `τ` (`J`), po czym łączy je w
`Λ = τ/ρ + J` — wskaźnik, który rośnie dla sygnałów "poszarpanych" fazowo
(szum, nierówności) i maleje dla gładkich, czystych tonów.

**Uczciwie o ograniczeniach:**

- To eksperymentalny wskaźnik bez ustalonej walidacji psychoakustycznej ani
  klinicznej — nie jest to uznana metryka jakości dźwięku.
- `ρ` może być bliskie zeru dla lokalnie płaskich fragmentów sygnału, co
  generuje rzadkie, ale bardzo duże wartości odstające w Λ. W testach
  zaobserwowano `max` rzędu 10⁵–10⁸ dla zwykłych sygnałów testowych — `mean`,
  `std`, `max`, `min` są więc silnie podatne na te odstające wartości.
  `median` jest znacznie stabilniejsza.
- Nawet `median` nie zawsze konsekwentnie maleje po wygładzeniu sygnału: w
  przykładzie `example_timdr_analysis.py` `std` spada o ~99.9% po
  `ultra_soft`, ale `median` w tym konkretnym przykładzie **wzrosła** — więc
  traktuj Λ jako pomocniczy, porównawczy sygnał do dalszej analizy, nie jako
  gotowy, jednoznaczny wskaźnik "czystości" dźwięku.

---

## 🧪 Testy

```
pip install pytest
pytest tests/ -v
```

44 testy, wszystkie przechodzą. Pokrycie: walidacja wejścia, wszystkie tryby
przetwarzania (w tym granice pasma zmierzone przez FFT), `auto_for_humans`
i jego reguły routingu (łącznie z udokumentowanym ograniczeniem detekcji
impulsów na głośnym tle), pełny zapis/odczyt WAV (w tym mono-downmix ze
stereo), wszystkie tryby przez `process_file` (w tym mieszanie dry/wet),
`j_clean` na sygnałach różnej długości (w tym bardzo krótkich), poprawka
przepełnienia int16 w `apply_gain_and_soften`, oraz `TIMDRAnalyzer`.

---

## 🐞 Naprawione błędy

Podczas przeglądu i pisania testów znaleziono i naprawiono:

1. **Biblioteka nie dała się w ogóle zaimportować na aktualnym scipy.**
   `from scipy.signal import hann` — `hann` zostało usunięte ze
   `scipy.signal` (przeniesione do `scipy.signal.windows`) w nowszych
   wersjach scipy. Na scipy 1.15 (aktualna w momencie tego przeglądu)
   `import easysound` kończył się natychmiastowym `ImportError`. Naprawione
   przez `from scipy.signal.windows import hann`.
2. **Brakująca zależność w `requirements.txt`.** `EasySound_JClean.py`
   importuje `matplotlib`, którego nie było na liście zależności — świeża
   instalacja `pip install -r requirements.txt` i uruchomienie GUI kończyło
   się `ModuleNotFoundError: No module named 'matplotlib'`. Dodane.
3. **`j_clean` wywalał się na krótkich sygnałach.** Dla sygnałów krótszych
   niż 513 próbek okno Hanninga bywało dłuższe niż sam sygnał (np. 221 vs
   220 próbek), co przez definicję `np.convolve(..., mode="same")` (długość
   wyniku = `max(len(a), len(v))`) dawało niedopasowane kształty tablic i
   `ValueError` przy końcowym mieszaniu z oryginałem. Naprawione przez
   wymuszenie długości okna ≤ długość sygnału.
4. **Przepełnienie int16 w GUI przy wysokim wzmocnieniu.** Suwak
   "Wzmocnienie" pozwala na 200%, a "Redukcja pików" na 100% (czyli brak
   dodatkowego ograniczenia). Oryginalny kod przycinał sygnał tylko do
   `max_val * soften` (gdzie `max_val` to JUŻ wzmocniona amplituda), a
   następnie rzutował wprost na `int16` bez ograniczenia do zakresu
   [-32767, 32767]. Przy tych ustawieniach wartości "zawijały się"
   (integer overflow) zamiast zostać ucięte, dając gwałtowne trzaski
   zamiast oczekiwanego, płynnego przycięcia. Zweryfikowane numerycznie:
   próbka o wartości 33739.8 dawała po prostym rzutowaniu `-31797` zamiast
   uciętego `+32767`. Naprawione — logika wydzielona do testowalnej funkcji
   `apply_gain_and_soften()` w `easysound.py`, z dodatkowym `clip` do
   zakresu int16 przed rzutowaniem.
5. **Niejasny błąd przy pustej tablicy.** `smooth_audio(np.array([]))` i
   podobne wywołania rzucały wewnętrzny, mylący błąd scipy zamiast czytelnej
   informacji. `_validate_signal` teraz jawnie odrzuca puste sygnały.
6. **Nieaktualna dokumentacja w poprzednim README.** Poprzednia wersja
   README opisywała funkcje, których nie było w kodzie (`EasySound` klasa z
   `tau/rho/J/Lambda` istniała tylko jako martwy fragment wklejony na końcu
   README, niepodłączony do żadnego pliku) — teraz jest to realnie
   zaimplementowana i przetestowana klasa `TIMDRAnalyzer`. Poprzednie README
   zawierało też podwójny, zduplikowany nagłówek `# EasySound` (efekt
   sklejenia dwóch wersji dokumentu) — poprawione. Usunięto też konkretne,
   niezweryfikowane liczby psychoakustyczne (np. "redukcja energii powyżej
   3.5 kHz", "wzmocnienie 1–3 kHz / formanty F2/F3") — kod wykonuje
   wygładzanie w dziedzinie czasu (moving average), a nie selektywne EQ
   pasmowe, więc te konkretne liczby nie odpowiadały faktycznemu działaniu
   algorytmów. Zastąpione zmierzonymi wartościami −3dB.

---

## ⚠️ Znane ograniczenia

- `_has_impulses` (używane przez `auto_for_humans`) porównuje szczyt do 4.5×
  mediana energii **całego** sygnału. Na głośnym tle (blisko pełnej skali)
  nawet wyraźny trzask może nie przekroczyć tego progu — patrz test
  `test_loud_carrier_masks_impulse_detection`. Dla cichszych nagrań z
  ostrymi trzaskami (typowy przypadek: winyl, nagrania terenowe) detekcja
  działa poprawnie.
- GUI (`EasySound_JClean.py`) wymaga środowiska z ekranem (Tkinter) i nie
  jest objęte testami automatycznymi — testom podlega wyłącznie wydzielona
  logika DSP (`j_clean`, `apply_gain_and_soften`), którą GUI importuje z
  `easysound.py`.
- Konwersja formatów innych niż WAV wymaga zewnętrznego `ffmpeg` — biblioteka
  go nie dostarcza ani nie sprawdza jego obecności przed próbą konwersji.
- `TIMDRAnalyzer` — patrz sekcja wyżej.

---

## ✔️ Status projektu

- 8 trybów/funkcji przetwarzania w bibliotece — zaimplementowane i
  przetestowane (44/44 testy przechodzą)
- Pipeline WAV (`load_wav`/`save_wav`/`process_file`, w tym dry/wet) —
  kompletny i przetestowany
- `j_clean` — przeniesiony z GUI do biblioteki, przetestowany na sygnałach
  różnej długości
- `TIMDRAnalyzer` — zaimplementowany, przetestowany, udokumentowany z
  uczciwymi zastrzeżeniami
- GUI (Live Preview, Waveform, J-Clean) — działa (zależy od Tkinter/ekranu),
  poprawka przepełnienia int16 zastosowana, logika DSP przetestowana
  pośrednio przez `easysound.py`
- 7 gotowych przykładów użycia w `examples/`

---

## 📦 Struktura plików

```
EasySound/
├── easysound.py              # kopia src/easysound.py (dla `import easysound`)
├── src/
│   └── easysound.py           # biblioteka: tryby przetwarzania, WAV I/O, j_clean, TIMDRAnalyzer
├── EasySound_JClean.py        # opcjonalne GUI (Tkinter + matplotlib + simpleaudio)
├── examples/                  # 7 gotowych, uruchamialnych przykładów
├── tests/
│   └── test_easysound.py      # 44 testy (pytest)
├── requirements.txt
├── pyproject.toml
├── index.html                 # prosta strona informacyjna
├── EasySound.png
└── LICENSE                    # MIT
```

---

## 📄 Licencja

MIT
