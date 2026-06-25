import matplotlib.pyplot as plt
import numpy as np

plt.figure(figsize=(10,4))

plt.title("Porównanie widma: oryginał vs ultra_soft")

plt.plot(freqs, orig_spectrum, label="oryginał")

plt.plot(freqs, ultra_spectrum, label="ultra_soft")

plt.xlim(0, 8000)

plt.legend()

plt.grid(True)

## Stabilność API

Od wersji 0.1.0 API jest stabilne:
- nazwy funkcji nie będą zmieniane,
- parametry wejściowe pozostaną kompatybilne,
- klasa EasySound będzie rozszerzana bez łamania istniejącego kodu.

## Wydajność

- Filtry IIR (Butterworth, sosfilt) działają w czasie O(n).
- AGC działa w jednym przebiegu (O(n)).
- Cały pipeline przetwarza 1 sekundę audio w ~0.3 ms (Ryzen 5).
- 
## Ograniczenia

- Brak time-stretchingu (planowane).
- Brak detekcji mowy (VAD).
- Brak adaptacyjnego filtra hałasu (ANC).

## Dlaczego nie FFmpeg filters?

FFmpeg oferuje filtry audio, ale:
- nie ma AGC z krótkim attack,
- nie ma psychoakustycznych presetów,
- nie ma trybu auto_for_humans,
- nie ma integracji z Python API.

EasySound jest warstwą DSP zoptymalizowaną pod percepcję, nie pod miks.

## Changelog

### 0.1.0
- pełna implementacja 6 trybów
- AGC, limiter, filtry IIR
- API obiektowe
- testy jednostkowe (38)
- przykłady
- nowa struktura projektu

## Roadmap

- 0.2.0 — time-stretching (APD)
- 0.3.0 — wzmocnienie 2–4 kHz (niedosłuch)
- 0.4.0 — VAD + adaptacyjne filtry
- 0.5.0 — GUI (EasySound Live)

