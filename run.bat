@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ===============================================
echo   EasySound - GUI (Live Preview + Waveform + J-Clean)
echo ===============================================
echo.

REM --- 0. Czy komenda "python" w ogole istnieje w PATH? ---
where python >nul 2>nul
if errorlevel 1 (
    echo BLAD: nie znaleziono komendy "python" w PATH.
    echo Zainstaluj Pythona z https://www.python.org/downloads/
    echo i podczas instalacji zaznacz "Add python.exe to PATH".
    goto END
)

python --version
echo.

REM --- 1. Utworz venv, jesli nie istnieje LUB jest niekompletny ---
if not exist venv\Scripts\activate.bat (
    echo [1/3] Tworze srodowisko wirtualne...
    python -m venv venv

    if not exist venv\Scripts\activate.bat (
        echo.
        echo BLAD: tworzenie venv nie powiodlo sie ^(brak pliku venv\Scripts\activate.bat^).
        echo.
        echo Najczestsza przyczyna na Windows 10/11: komenda "python" wskazuje na
        echo alias Microsoft Store zamiast prawdziwej instalacji Pythona ^(wyglada
        echo na dzialajaca, ale nic realnie nie robi^). Sprawdz:
        echo   Ustawienia - Aplikacje - Zaawansowane opcje aplikacji
        echo   - Aliasy wykonywania aplikacji - wylacz alias dla "python.exe" i "python3.exe"
        echo a nastepnie zainstaluj Pythona z https://www.python.org/downloads/
        goto END
    )
) else (
    echo [1/3] Srodowisko wirtualne juz istnieje, pomijam tworzenie.
)

call venv\Scripts\activate.bat
if not defined VIRTUAL_ENV (
    echo BLAD: aktywacja venv nie powiodla sie ^(call venv\Scripts\activate.bat^).
    goto END
)

REM --- 2. Zaleznosci (BEZ --quiet, zeby bledy byly widoczne) ---
echo [2/3] Instaluje zaleznosci z requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo BLAD: instalacja zaleznosci nie powiodla sie - patrz komunikaty pip powyzej.
    goto END
)

REM --- 3. Sprawdzenie ffmpeg (opcjonalne, tylko dla formatow innych niz WAV) ---
where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo.
    echo UWAGA: nie znaleziono "ffmpeg" w PATH. Program uruchomi sie poprawnie,
    echo ale wczytywanie plikow innych niz WAV ^(MP3, M4A, FLAC, OGG^) nie bedzie
    echo dzialac, dopoki nie dodasz ffmpeg.exe do PATH lub do tego folderu.
    echo Pobierz z: https://ffmpeg.org/download.html
    echo.
)

REM --- 4. Start GUI ---
echo.
echo [3/3] Uruchamiam EasySound GUI...
echo.

python EasySound_JClean.py

if errorlevel 1 (
    echo.
    echo BLAD: EasySound_JClean.py zakonczyl sie bledem - patrz komunikaty powyzej.
)

:END
echo.
echo ===============================================
echo Nacisnij dowolny klawisz, zeby zamknac to okno...
pause >nul
