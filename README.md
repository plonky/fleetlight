# Fleetlight

A device-agnostic lighting **effects engine** for Home Assistant.

Philips Hue has dynamic scenes. WLED has real-time UDP sync. Neither works
across a mixed fleet of lights — Zigbee, WiFi, different brands, different
protocols — the kind of setup most real Home Assistant installs actually
have. Fleetlight sits on top of HA and runs procedural effects (a color
wave, a thunderstorm flicker, ...) across *any* set of `light.*` entities,
adapting to however many lights you actually give it instead of hardcoding
per-bulb logic.

## Status

Early. One effect (`wave`) exists end-to-end as a proof of the architecture.
More effects, a real HACS release, and hardware-tested rate limiting are
still to come.

## How it works

- **Zones** are an ordered set of lights, defined via the config flow.
  Order matters for effects like the wave that flow across lights in
  sequence. Pick a Home Assistant **Area** for a quick default order, or
  pick lights individually (in order) to override it.
- Each zone becomes a `switch` entity. Turning it on/off starts/stops
  whichever effect was last used.
- The `fleetlight.start_effect` service picks the effect and lets you tune
  its parameters:

  ```yaml
  service: fleetlight.start_effect
  target:
    entity_id: switch.living_room_zone_effect
  data:
    effect: wave
    params:
      speed: 3.0
      width_fraction: 0.25
      color: [255, 200, 120]
      min_brightness: 20
      max_brightness: 255
  ```

  ```yaml
  service: fleetlight.stop_effect
  target:
    entity_id: switch.living_room_zone_effect
  ```

## Effects

- **wave** — a brightness peak that travels along the zone's light order
  and loops continuously. Wave width scales with light count, so it reads
  as one coherent wave whether the zone has 3 lights or 30.

## Installation

### HACS (custom repository, until this is in the default store)

1. HACS → Integrations → ⋮ → Custom repositories → add this repo URL,
   category "Integration".
2. Install "Fleetlight", restart Home Assistant.
3. Settings → Devices & Services → Add Integration → "Fleetlight".

### Manual

Copy `custom_components/fleetlight` into your Home Assistant `config/custom_components/` directory and restart.

## Development

```bash
pip install -r requirements_test.txt
pytest
```

Tests run against mocked light entities via
[`pytest-homeassistant-custom-component`](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)
— no real Home Assistant instance or hardware required.

## License

MIT
