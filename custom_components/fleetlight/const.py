"""Constants for the Fleetlight integration."""

DOMAIN = "fleetlight"
PLATFORMS = ["switch"]

CONF_AREA_ID = "area_id"
CONF_LIGHT_ENTITY_IDS = "light_entity_ids"

DEFAULT_EFFECT = "wave"

SERVICE_START_EFFECT = "start_effect"
SERVICE_STOP_EFFECT = "stop_effect"

ATTR_EFFECT = "effect"
ATTR_PARAMS = "params"

# Minimum spacing between individual light.turn_on calls dispatched by the
# engine, to avoid flooding a Zigbee/WiFi mesh with a burst of commands.
MIN_COMMAND_INTERVAL = 0.05
