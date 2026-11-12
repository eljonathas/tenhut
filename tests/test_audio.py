from typing import ClassVar

import pygame
import pytest

from tenhut.game.audio import Note, SoundBank, SoundEffect, SoundRecipe, ToneSynth, VolumeCurve, Waveform


class FakeSound:
    created: ClassVar[list["FakeSound"]] = []

    def __init__(self, buffer: bytes) -> None:
        self.buffer = buffer
        self.volume = None
        self.plays = 0
        FakeSound.created.append(self)

    def set_volume(self, volume: float) -> None:
        self.volume = volume

    def play(self) -> None:
        self.plays += 1


@pytest.fixture
def mixer(monkeypatch):
    FakeSound.created = []
    monkeypatch.setattr(pygame.mixer, "init", lambda *args: None)
    monkeypatch.setattr(pygame.mixer, "Sound", FakeSound)
    return FakeSound


def sound_of(effect: SoundEffect) -> FakeSound:
    return FakeSound.created[list(SoundEffect).index(effect)]


def test_every_effect_has_a_recipe_with_notes_and_a_gain():
    for effect in SoundEffect:
        assert effect.recipe.notes and 0 < effect.recipe.gain <= 1


@pytest.mark.parametrize("effect", list(SoundEffect))
def test_synthesized_length_matches_the_note_durations(effect):
    samples = len(ToneSynth().synthesize(effect.recipe)) // 2
    expected = sum(int(ToneSynth.SAMPLE_RATE * note.duration) for note in effect.recipe.notes)
    assert samples == expected


def test_synthesis_peaks_at_half_scale_and_rests_are_silent():
    recipe = SoundRecipe(Waveform.SQUARE, (Note(440, 0.1), Note.rest(0.05)), 1.0)
    pcm = ToneSynth().synthesize(recipe)
    values = [int.from_bytes(pcm[i : i + 2], "little", signed=True) for i in range(0, len(pcm), 2)]
    tone, rest = values[:2205], values[2205:]
    assert max(tone) == pytest.approx(32767 * ToneSynth.PEAK_FRACTION, abs=1)
    assert set(rest) == {0}


def test_notes_fade_in_and_out_without_clicking():
    recipe = SoundRecipe(Waveform.TRIANGLE, (Note(440, 0.1),), 1.0)
    pcm = ToneSynth().synthesize(recipe)
    assert int.from_bytes(pcm[:2], "little", signed=True) == 0
    assert abs(int.from_bytes(pcm[-2:], "little", signed=True)) < 600


@pytest.mark.parametrize(
    ("waveform", "phase", "expected"),
    [
        (Waveform.SQUARE, 0.25, 1.0),
        (Waveform.SQUARE, 0.75, -1.0),
        (Waveform.TRIANGLE, 0.0, -1.0),
        (Waveform.TRIANGLE, 0.25, 0.0),
        (Waveform.TRIANGLE, 0.5, 1.0),
    ],
)
def test_waveform_samples(waveform, phase, expected):
    assert waveform.sample(phase) == pytest.approx(expected)


def test_volume_curve_is_perceptual():
    curve = VolumeCurve()
    assert curve.level(0) == 0 and curve.level(100) == 1
    assert curve.level(50) == pytest.approx(0.5**1.5)
    assert curve.level(25) < 0.25


def test_each_effect_is_scaled_by_master_volume_and_its_own_gain(mixer):
    bank = SoundBank(True, 50)
    for effect in SoundEffect:
        assert sound_of(effect).volume == pytest.approx(0.5**1.5 * effect.recipe.gain)
    bank.set_volume(250)
    assert bank.volume == 100 and sound_of(SoundEffect.CLICK).volume == pytest.approx(SoundEffect.CLICK.recipe.gain)


def test_play_respects_enabled_and_volume(mixer):
    bank = SoundBank(True, 40)
    bank.play(SoundEffect.CLICK)
    assert sound_of(SoundEffect.CLICK).plays == 1
    bank.enabled = False
    bank.play(SoundEffect.CLICK)
    bank.enabled = True
    bank.set_volume(0)
    bank.play(SoundEffect.CLICK)
    assert sound_of(SoundEffect.CLICK).plays == 1


def test_no_audio_device_leaves_a_silent_bank(monkeypatch):
    def fail(*args):
        raise pygame.error("no device")

    monkeypatch.setattr(pygame.mixer, "init", fail)
    bank = SoundBank(True, 40)
    bank.play(SoundEffect.CLICK)
    assert not bank.enabled and not bank.available
