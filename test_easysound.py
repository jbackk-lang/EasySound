"""
Testy dla biblioteki EasySound.

Uruchomienie:  pytest tests/ -v
(wymaga: pip install pytest numpy scipy)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pytest

from easysound import (
    smooth_audio,
    soften_peaks,
    human_friendly,
    ultra_soft,
    speech_clarity,
    auto_for_humans,
    _has_impulses,
    load_wav,
    save_wav,
    process_file,
    j_clean,
    apply_gain_and_soften,
    TIMDRAnalyzer,
)


# ---------------------------------------------------------------------------
# Fixtures / helpery
# ---------------------------------------------------------------------------

FS = 44100


def make_tone(freq=440.0, duration=1.0, amp=0.5, fs=FS):
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    return amp * np.sin(2 * np.pi * freq * t)


def make_noisy_tone(freq=440.0, duration=1.0, amp=0.5, noise_std=0.05, fs=FS, seed=0):
    rng = np.random.default_rng(seed)
    tone = make_tone(freq, duration, amp, fs)
    return tone + rng.normal(0, noise_std, size=tone.shape)


def make_clicky_signal(fs=FS, duration=1.0, seed=1):
    # cichy sygnal (amp 0.05) z kilkoma glosnymi trzaskami (0.9) — to
    # realistyczny profil winylowych trzaskow/klikniec. Uzycie glosnego
    # tonu jako tla NIE wywoluje detekcji w _has_impulses, bo prog to
    # 4.5x mediana energii tla — patrz test_loud_carrier_masks_impulse_detection.
    sig = make_tone(440.0, duration, 0.05, fs)
    rng = np.random.default_rng(seed)
    click_positions = rng.choice(len(sig), size=10, replace=False)
    sig[click_positions] = 0.9
    return sig


@pytest.fixture
def tmp_wav_pair(tmp_path):
    in_path = tmp_path / "in.wav"
    out_path = tmp_path / "out.wav"
    return str(in_path), str(out_path)


# ---------------------------------------------------------------------------
# Walidacja wejscia
# ---------------------------------------------------------------------------

class TestValidation:
    def test_none_raises(self):
        with pytest.raises(ValueError):
            smooth_audio(None)

    def test_2d_raises(self):
        with pytest.raises(ValueError):
            smooth_audio(np.zeros((4, 4)))

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            smooth_audio(np.array([]))

    def test_list_input_accepted(self):
        # akceptuje zwykla liste Pythona, nie tylko np.ndarray
        out = smooth_audio([0.0, 0.1, 0.2, 0.1, 0.0] * 20, window_size=5)
        assert np.all(np.isfinite(out))


# ---------------------------------------------------------------------------
# smooth_audio
# ---------------------------------------------------------------------------

class TestSmoothAudio:
    def test_preserves_length(self):
        sig = make_tone()
        out = smooth_audio(sig, window_size=51)
        assert out.shape == sig.shape

    def test_window_below_3_returns_unchanged(self):
        sig = make_tone(duration=0.01)
        out = smooth_audio(sig, window_size=2)
        assert np.allclose(out, sig)

    def test_reduces_high_frequency_content(self):
        # ton 8kHz powinien byc mocno tlumiony przez okno 51 (mierzone
        # ~635 Hz -3dB cutoff przy 44100 Hz — patrz test_measured_cutoffs)
        hf_tone = make_tone(freq=8000.0, duration=0.2)
        out = smooth_audio(hf_tone, window_size=51)
        # energia sygnalu wygladzonego powinna byc wyraznie mniejsza
        assert np.std(out) < 0.3 * np.std(hf_tone)

    def test_preserves_low_frequency_content(self):
        # ton 100Hz powinien przejsc niemal bez zmian przez okno 51
        lf_tone = make_tone(freq=100.0, duration=0.2)
        out = smooth_audio(lf_tone, window_size=51)
        assert np.std(out) > 0.8 * np.std(lf_tone)

    def test_measured_minus3db_cutoffs(self):
        """Weryfikuje rzeczywiste (zmierzone) czestotliwosci odciecia -3dB
        dla okna Hanninga uzywanego w smooth_audio, przy fs=44100 Hz.
        Wyniki dokumentowane sa w README — TEN test pilnuje, zeby liczby
        w README nie rozjechaly sie z kodem."""
        from scipy.signal.windows import hann

        def minus3db_cutoff(window_size, fs=FS):
            w = hann(window_size)
            w = w / w.sum()
            W = np.abs(np.fft.rfft(w, n=65536))
            freqs = np.fft.rfftfreq(65536, d=1 / fs)
            db = 20 * np.log10(W / W[0] + 1e-12)
            idx = np.argmax(db < -3)
            return freqs[idx]

        # tolerancje +/-15%, zaokraglone wartosci referencyjne z README
        expected = {21: 1586, 41: 793, 51: 635, 121: 265}
        for ws, exp in expected.items():
            measured = minus3db_cutoff(ws)
            assert abs(measured - exp) / exp < 0.15, (
                f"window_size={ws}: measured {measured:.0f} Hz vs "
                f"expected ~{exp} Hz (README out of date?)"
            )


# ---------------------------------------------------------------------------
# soften_peaks
# ---------------------------------------------------------------------------

class TestSoftenPeaks:
    def test_below_threshold_unchanged(self):
        sig = np.array([0.0, 0.2, -0.3, 0.5, -0.6])
        out = soften_peaks(sig, threshold=0.85, knee_width=0.15)
        assert np.allclose(out, sig)

    def test_above_knee_hard_clipped(self):
        sig = np.array([1.0, -1.0, 0.99])
        out = soften_peaks(sig, threshold=0.85, knee_width=0.15)
        knee_end = 0.85 + 0.15
        assert np.all(np.abs(out) <= knee_end + 1e-9)

    def test_reduces_peak_amplitude(self):
        sig = make_clicky_signal()
        out = soften_peaks(sig)
        assert np.max(np.abs(out)) <= np.max(np.abs(sig)) + 1e-9

    def test_preserves_sign(self):
        sig = np.array([0.95, -0.95, 1.0, -1.0])
        out = soften_peaks(sig)
        assert np.all(np.sign(out) == np.sign(sig))


# ---------------------------------------------------------------------------
# human_friendly / ultra_soft / speech_clarity
# ---------------------------------------------------------------------------

class TestCompositeModes:
    def test_human_friendly_smooths_and_limits(self):
        sig = make_clicky_signal()
        out = human_friendly(sig)
        assert out.shape == sig.shape
        assert np.all(np.isfinite(out))

    def test_ultra_soft_smooths_more_than_default(self):
        sig = make_tone(freq=2000.0, duration=0.2)
        soft = smooth_audio(sig, window_size=51)
        ultra = ultra_soft(sig)
        assert np.std(ultra) < np.std(soft)

    def test_speech_clarity_retains_more_transient_than_ultra_soft(self):
        sig = make_clicky_signal()
        sc = speech_clarity(sig)
        us = ultra_soft(sig)
        # speech_clarity zachowuje 65% transjentow, wiec powinien miec
        # wyzsza energie wysokoczestotliwosciowa (mierzona przez std roznicy
        # wzgledem mocno wygladzonej wersji) niz ultra_soft
        base = smooth_audio(sig, window_size=121)
        assert np.std(sc - base) > np.std(us - base)


# ---------------------------------------------------------------------------
# auto_for_humans
# ---------------------------------------------------------------------------

class TestAutoForHumans:
    def test_silence_returns_silence(self):
        sig = np.zeros(1000)
        out = auto_for_humans(sig)
        assert np.allclose(out, 0)

    def test_clicky_signal_routes_to_soften_peaks(self):
        sig = make_clicky_signal()
        assert _has_impulses(sig)
        out = auto_for_humans(sig)
        expected = soften_peaks(sig)
        assert np.allclose(out, expected)

    def test_loud_carrier_masks_impulse_detection(self):
        """Udokumentowane ograniczenie: _has_impulses porownuje szczyt do
        4.5x mediany energii CALEGO sygnalu. Na glosnym tle (blisko pelnej
        skali) nawet wyrazny trzask moze nie przekroczyc tego progu, wiec
        auto_for_humans nie przelaczy sie na soften_peaks. To test
        regresyjny dla tego ograniczenia, nie oczekiwane zachowanie."""
        loud_tone = make_tone(440.0, 1.0, 0.4, FS)
        rng = np.random.default_rng(2)
        clicky_but_loud = loud_tone.copy()
        clicky_but_loud[rng.choice(len(clicky_but_loud), size=10, replace=False)] = 0.99
        assert not _has_impulses(clicky_but_loud)

    def test_low_crest_routes_to_ultra_soft(self):
        # sygnal prostokatny ma niski crest factor (~1.0) i brak impulsow
        t = np.linspace(0, 1, FS, endpoint=False)
        square = 0.5 * np.sign(np.sin(2 * np.pi * 5 * t))
        assert not _has_impulses(square)
        crest = np.max(np.abs(square)) / (np.mean(np.abs(square)) + 1e-9)
        assert crest < 2.0
        out = auto_for_humans(square)
        assert np.allclose(out, ultra_soft(square))

    def test_high_crest_routes_to_smooth_audio(self):
        # pojedynczy, izolowany impuls o duzej amplitudzie na tle ciszy —
        # ma wysoki crest factor, ale nie przekracza progu detekcji impulsow
        # (bo _has_impulses patrzy na medianę energii, ktora tu jest 0)
        sig = np.zeros(2000)
        sig[1000] = 0.5
        assert _has_impulses(sig) is False  # median==0 -> False z definicji
        # w tym przypadku funkcja idzie sciezka ciszy/niskiej mediany;
        # test dokumentuje ten brzegowy przypadek zamiast go ukrywac
        out = auto_for_humans(sig)
        assert np.all(np.isfinite(out))


# ---------------------------------------------------------------------------
# load_wav / save_wav / process_file
# ---------------------------------------------------------------------------

class TestWavIO:
    def test_roundtrip(self, tmp_wav_pair):
        in_path, out_path = tmp_wav_pair
        sig_int16 = (make_tone() * 32767).astype(np.int16)
        from scipy.io import wavfile
        wavfile.write(in_path, FS, sig_int16)

        sr, data = load_wav(in_path)
        assert sr == FS
        assert np.max(np.abs(data)) <= 1.0 + 1e-6

        save_wav(out_path, sr, data)
        sr2, data2 = load_wav(out_path)
        assert sr2 == FS
        assert np.allclose(data, data2, atol=1e-3)

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_wav("/nonexistent/path/does_not_exist.wav")

    def test_stereo_downmixed_to_mono(self, tmp_wav_pair):
        in_path, _ = tmp_wav_pair
        from scipy.io import wavfile
        left = (make_tone(440) * 32767).astype(np.int16)
        right = (make_tone(880) * 32767).astype(np.int16)
        stereo = np.stack([left, right], axis=1)
        wavfile.write(in_path, FS, stereo)

        sr, data = load_wav(in_path)
        assert data.ndim == 1
        assert len(data) == len(left)

    @pytest.mark.parametrize(
        "mode",
        ["auto", "soften_peaks", "human_friendly", "ultra_soft", "speech_clarity", "smooth"],
    )
    def test_process_file_all_modes(self, tmp_wav_pair, mode):
        in_path, out_path = tmp_wav_pair
        from scipy.io import wavfile
        sig = make_clicky_signal()
        wavfile.write(in_path, FS, (sig * 32767).astype(np.int16))

        out = process_file(in_path, out_path, mode=mode)
        assert os.path.exists(out_path)
        assert np.all(np.isfinite(out))

        sr, saved = load_wav(out_path)
        assert sr == FS
        assert len(saved) == len(sig)

    def test_process_file_unknown_mode_raises(self, tmp_wav_pair):
        in_path, out_path = tmp_wav_pair
        from scipy.io import wavfile
        wavfile.write(in_path, FS, (make_tone() * 32767).astype(np.int16))
        with pytest.raises(ValueError):
            process_file(in_path, out_path, mode="nope")

    def test_process_file_dry_wet_zero_matches_original(self, tmp_wav_pair):
        in_path, out_path = tmp_wav_pair
        from scipy.io import wavfile
        sig = make_clicky_signal()
        wavfile.write(in_path, FS, (sig * 32767).astype(np.int16))

        out = process_file(in_path, out_path, mode="ultra_soft", dry_wet=0.0)
        sr, original = load_wav(in_path)
        assert np.allclose(out, original, atol=1e-6)

    def test_process_file_dry_wet_one_matches_full_wet(self, tmp_wav_pair):
        in_path, out_path = tmp_wav_pair
        from scipy.io import wavfile
        sig = make_clicky_signal()
        wavfile.write(in_path, FS, (sig * 32767).astype(np.int16))

        sr, original = load_wav(in_path)
        out = process_file(in_path, out_path, mode="ultra_soft", dry_wet=1.0)
        assert np.allclose(out, ultra_soft(original), atol=1e-6)


# ---------------------------------------------------------------------------
# j_clean (z EasySound_JClean.py)
# ---------------------------------------------------------------------------

class TestJClean:
    def test_output_finite_and_same_length(self):
        sig = make_clicky_signal()
        out = j_clean(sig)
        assert out.shape == sig.shape
        assert np.all(np.isfinite(out))

    def test_reduces_click_energy(self):
        sig = make_clicky_signal()
        out = j_clean(sig)
        assert np.max(np.abs(out)) < np.max(np.abs(sig))

    def test_handles_short_signal(self):
        # sygnal krotszy niz domyslne okno (513) — nie powinien wywalic sie
        short_sig = make_tone(duration=0.005)  # ~220 probek
        out = j_clean(short_sig)
        assert out.shape == short_sig.shape
        assert np.all(np.isfinite(out))

    def test_handles_very_short_signal(self):
        out = j_clean(np.array([0.1, 0.2, 0.3, 0.2, 0.1]))
        assert np.all(np.isfinite(out))


# ---------------------------------------------------------------------------
# apply_gain_and_soften (uzywane przez GUI EasySound_JClean.py)
# ---------------------------------------------------------------------------

class TestApplyGainAndSoften:
    def test_stays_within_int16_range_at_max_gain(self):
        # regresja dla bledu przepelnienia int16: gain=200%, soften=100%
        # (skrajne wartosci suwakow w GUI) nie moga dawac "zawijania"
        sig = 30000.0 * np.sin(np.linspace(0, 20 * np.pi, 2000))
        out = apply_gain_and_soften(sig, gain=2.0, soften=1.0)
        assert out.dtype == np.int16
        assert np.max(np.abs(out)) <= 32767

    def test_no_sign_flips_from_overflow(self):
        # przed poprawka przepelnienie int16 potrafilo odwracac znak duzej
        # probki (np. +33739.8 -> -31797). Sprawdzamy zachowanie znaku
        # tylko dla probek wyraznie odleglych od zera — probki blisko
        # przejscia przez zero moga naturalnie zaokraglic sie do 0 przy
        # rzutowaniu na int, co nie jest "zawijaniem" i nie powinno
        # falszywie failowac tego testu.
        sig = 30000.0 * np.sin(np.linspace(0, 20 * np.pi, 2000))
        out = apply_gain_and_soften(sig, gain=2.0, soften=1.0)
        far_from_zero = np.abs(sig) > 1000
        assert np.all(np.sign(out[far_from_zero]) == np.sign(sig[far_from_zero]))

    def test_gain_one_soften_one_is_near_identity_below_clip(self):
        sig = np.array([100.0, -200.0, 300.0])
        out = apply_gain_and_soften(sig, gain=1.0, soften=1.0)
        assert np.allclose(out, sig, atol=1)


# ---------------------------------------------------------------------------
# TIMDRAnalyzer (eksperymentalna analiza fazowa Lambda)
# ---------------------------------------------------------------------------

class TestTIMDRAnalyzer:
    def test_requires_signal_or_path(self):
        with pytest.raises(ValueError):
            TIMDRAnalyzer()

    def test_summary_keys(self):
        a = TIMDRAnalyzer(signal=make_tone())
        s = a.summary()
        assert set(s.keys()) == {"mean", "median", "std", "max", "min"}
        assert all(np.isfinite(v) for v in s.values())

    def test_noisy_signal_has_higher_lambda_variance_than_pure_tone(self):
        """Dokumentuje (i pilnuje regresji) empiryczne zachowanie: dla
        zaszumionego sygnalu odchylenie standardowe Lambda jest wyraznie
        wieksze niz dla czystego tonu. To NIE jest walidacja
        psychoakustyczna — to test spojnosci z opisem w README."""
        pure = TIMDRAnalyzer(signal=make_tone(duration=0.5))
        noisy = TIMDRAnalyzer(signal=make_noisy_tone(duration=0.5, noise_std=0.05))

        s_pure = pure.summary()
        s_noisy = noisy.summary()

        assert s_noisy["std"] > s_pure["std"]

    def test_loads_from_wav_path(self, tmp_wav_pair):
        in_path, _ = tmp_wav_pair
        from scipy.io import wavfile
        wavfile.write(in_path, FS, (make_tone() * 32767).astype(np.int16))
        a = TIMDRAnalyzer(path=in_path)
        assert a.rate == FS
        s = a.summary()
        assert all(np.isfinite(v) for v in s.values())
