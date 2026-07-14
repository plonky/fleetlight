"""Pure unit tests for the thunderstorm effect's math - no HA instance needed."""

from custom_components.fleetlight.effects.thunderstorm import ThunderstormEffect


def test_lights_flicker_independently():
    effect = ThunderstormEffect({"seed": 1, "flash_probability": 0.0})
    states = effect.step(t=0.3, light_count=8)

    brightnesses = {s.brightness for s in states}
    assert len(brightnesses) > 1


def test_no_flash_stays_within_base_range():
    effect = ThunderstormEffect(
        {"seed": 1, "flash_probability": 0.0, "min_brightness": 15, "max_brightness": 90}
    )
    for tenth in range(50):
        for state in effect.step(t=tenth / 10, light_count=10):
            assert 15 <= state.brightness <= 90
            assert state.rgb_color == (80, 130, 220)


def test_certain_flash_produces_flash_color_and_higher_brightness():
    effect = ThunderstormEffect(
        {
            "seed": 1,
            "flash_probability": 1.0,
            "max_brightness": 90,
            "flash_brightness": 255,
            "flash_duration": 0.25,
        }
    )
    # Right at the start of a flash bucket, decay ~= 1, so brightness should
    # be pulled sharply toward flash_brightness and color toward flash_color.
    states = effect.step(t=0.0, light_count=5)
    assert any(s.brightness > 90 for s in states)
    assert any(s.rgb_color == (255, 250, 220) for s in states)


def test_different_seeds_diverge():
    effect_a = ThunderstormEffect({"seed": 1})
    effect_b = ThunderstormEffect({"seed": 2})

    states_a = effect_a.step(t=0.3, light_count=10)
    states_b = effect_b.step(t=0.3, light_count=10)

    assert [s.brightness for s in states_a] != [s.brightness for s in states_b]


def test_empty_zone_returns_no_states():
    effect = ThunderstormEffect({"seed": 1})
    assert effect.step(t=0.0, light_count=0) == []
