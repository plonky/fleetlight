"""Pure unit tests for the wave effect's math - no HA instance needed."""

from custom_components.fleetlight.effects.wave import WaveEffect


def test_wave_peaks_at_center_light():
    effect = WaveEffect({"speed": 0.0})  # frozen wave, center = index 0
    states = effect.step(t=0.0, light_count=9)

    brightnesses = [s.brightness for s in states]
    assert brightnesses[0] == max(brightnesses)


def test_wave_moves_over_time():
    effect = WaveEffect({"speed": 2.0})
    early = effect.step(t=0.0, light_count=20)
    later = effect.step(t=1.0, light_count=20)

    peak_index_early = max(range(20), key=lambda i: early[i].brightness)
    peak_index_later = max(range(20), key=lambda i: later[i].brightness)

    assert peak_index_early != peak_index_later


def test_wave_width_scales_with_light_count():
    effect = WaveEffect({"speed": 0.0, "width_fraction": 0.2})

    small = effect.step(t=0.0, light_count=5)
    large = effect.step(t=0.0, light_count=50)

    def bright_span(states, threshold=100):
        return sum(1 for s in states if s.brightness >= threshold)

    small_span = bright_span(small)
    large_span = bright_span(large)

    # Proportionally, a bigger zone should light up a wider absolute swath,
    # not the same fixed handful of lights every time.
    assert large_span > small_span


def test_wave_respects_brightness_bounds():
    effect = WaveEffect(
        {"speed": 0.0, "min_brightness": 30, "max_brightness": 200}
    )
    states = effect.step(t=0.0, light_count=10)

    for state in states:
        assert 30 <= state.brightness <= 200


def test_wave_empty_zone_returns_no_states():
    effect = WaveEffect()
    assert effect.step(t=0.0, light_count=0) == []
