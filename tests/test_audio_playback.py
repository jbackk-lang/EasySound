"""Testy dla src/audio_playback.py.

Celowo NIE testujemy `play_audio()` bezposrednio (wymaga PortAudio +
fizycznej/wirtualnej karty dzwiekowej, ktorej nie ma w srodowisku CI).
`decode_audio()` jest czysta funkcja bez zaleznosci od sounddevice i to
ja pokrywaja testy ponizej.

Wymaga zainstalowanego `ffmpeg` w PATH (dla plikow MP3/M4A) — testy dla
tych formatow sa pomijane (`pytest.skip`), jesli ffmpeg nie jest dostepny.
"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pytest
from scipy.io import wavfile

from audio_playback import decode_audio

FFMPEG_AVAILABLE = shutil.which("ffmpeg") is not None

FS = 44100


def _make_wav(path, fs=FS, duration=1.0, amp=0.3, freq=440.0):
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    sig = (amp * np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)
    wavfile.write(path, fs, sig)
    return sig, fs


def _ffmpeg_convert(src, dst, extra_args=None):
    cmd = ["ffmpeg", "-y", "-i", src] + (extra_args or []) + [dst]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


@pytest.fixture
def wav_16bit_mono(tmp_path):
    path = str(tmp_path / "mono16.wav")
    _make_wav(path)
    return path


@pytest.fixture
def wav_16bit_stereo(tmp_path):
    path = str(tmp_path / "stereo16.wav")
    fs = FS
    t = np.linspace(0, 1.0, fs, endpoint=False)
    left = (0.3 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    right = (0.3 * np.sin(2 * np.pi * 660 * t) * 32767).astype(np.int16)
    wavfile.write(path, fs, np.stack([left, right], axis=1))
    return path


class TestDecodeAudioWav:
    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            decode_audio("/nonexistent/path/nope.wav")

    def test_mono_wav_normalized_range(self, wav_16bit_mono):
        data, fs = decode_audio(wav_16bit_mono)
        assert fs == FS
        assert data.ndim == 1
        assert np.max(np.abs(data)) <= 1.0 + 1e-6
        assert np.max(np.abs(data)) > 0.2  # amp=0.3 powinno przetrwac dekodowanie

    def test_stereo_wav_shape(self, wav_16bit_stereo):
        data, fs = decode_audio(wav_16bit_stereo)
        assert data.ndim == 2
        assert data.shape[1] == 2

    @pytest.mark.parametrize("codec_args,label", [
        (["-acodec", "pcm_u8"], "8bit"),
        (["-acodec", "pcm_s16le"], "16bit"),
        (["-acodec", "pcm_s24le"], "24bit"),
        (["-acodec", "pcm_s32le"], "32bit"),
    ])
    def test_wav_various_bit_depths(self, tmp_path, wav_16bit_mono, codec_args, label):
        if not FFMPEG_AVAILABLE:
            pytest.skip("ffmpeg not available")
        out_path = str(tmp_path / f"conv_{label}.wav")
        _ffmpeg_convert(wav_16bit_mono, out_path, codec_args)

        data, fs = decode_audio(out_path)
        assert fs == FS
        assert np.all(np.isfinite(data))
        # amplituda powinna byc w rozsadnym zakresie [-1,1] niezaleznie od
        # bitowej glebi zrodla — to wlasnie ten aspekt byl zepsuty w
        # oryginalnym kodzie (sztywne zalozenie dtype=int16)
        assert np.max(np.abs(data)) <= 1.0 + 1e-3
        assert np.max(np.abs(data)) > 0.15


@pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="ffmpeg not available")
class TestDecodeAudioCompressed:
    def test_mp3_roundtrip_amplitude(self, tmp_path, wav_16bit_mono):
        mp3_path = str(tmp_path / "test.mp3")
        _ffmpeg_convert(wav_16bit_mono, mp3_path)

        data, fs = decode_audio(mp3_path)
        assert fs == FS
        assert data.ndim == 1
        assert np.max(np.abs(data)) <= 1.0 + 1e-3
        assert np.max(np.abs(data)) > 0.15

    def test_m4a_roundtrip_amplitude(self, tmp_path, wav_16bit_mono):
        m4a_path = str(tmp_path / "test.m4a")
        _ffmpeg_convert(wav_16bit_mono, m4a_path, ["-c:a", "aac"])

        data, fs = decode_audio(m4a_path)
        assert fs == FS
        assert np.max(np.abs(data)) <= 1.0 + 1e-3

    def test_lossless_alac_24bit_m4a_regression(self, tmp_path, wav_16bit_mono):
        """Test regresyjny dla znalezionego bledu: oryginalny kod uzywal
        `np.frombuffer(raw, dtype=np.int16)` bez sprawdzenia
        `sample_width`. Bezstratny ALAC w kontenerze .m4a jest dekodowany
        przez pydub jako sample_width=4 (32-bit), wiec sztywne zalozenie
        int16 dawalo dwukrotnie za dlugi, kompletnie zaszumiony sygnal
        (kazda 4-bajtowa probka byla blednie odczytywana jako dwie
        2-bajtowe). Zweryfikowane bezposrednio: buggy decode dawal
        len=88200 zamiast poprawnych 44100 probek, z zakresem wartosci
        odpowiadajacym szumowi, nie oryginalnemu tonowi."""
        # 24-bit zrodlo
        wav24_path = str(tmp_path / "src24.wav")
        _ffmpeg_convert(wav_16bit_mono, wav24_path, ["-acodec", "pcm_s24le"])

        alac_path = str(tmp_path / "test_alac24.m4a")
        _ffmpeg_convert(wav24_path, alac_path, ["-c:a", "alac"])

        data, fs = decode_audio(alac_path)
        assert fs == FS
        # poprawna dlugosc: ~44100 probek (ta sama dlugosc co zrodlo), NIE
        # ~88200 (co dawal blad podwojnego odczytu 4-bajtowych probek jako
        # pary 2-bajtowych)
        assert abs(len(data) - FS) < FS * 0.05, (
            f"expected ~{FS} samples, got {len(data)} — mozliwy powrot bledu "
            f"zlego mapowania sample_width -> dtype"
        )
        assert np.max(np.abs(data)) <= 1.0 + 1e-3
        assert np.max(np.abs(data)) > 0.15

    def test_unreadable_file_raises_valueerror(self, tmp_path):
        bad_path = tmp_path / "not_audio.mp3"
        bad_path.write_bytes(b"this is not an mp3 file at all")
        with pytest.raises(ValueError):
            decode_audio(str(bad_path))
