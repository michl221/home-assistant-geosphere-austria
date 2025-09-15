"""The GeoSphere Austria Prediction integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import (
    GeoSphereAustriaPredictionConfigEntry,
    GeoSphereAustriaPredictionUpdateCoordinator,
)

_PLATFORMS: list[Platform] = [Platform.WEATHER]


async def async_setup_entry(
    hass: HomeAssistant, entry: GeoSphereAustriaPredictionConfigEntry
) -> bool:
    """Set up GeoSphere Austria Prediction from a config entry."""

    coordinator = GeoSphereAustriaPredictionUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: GeoSphereAustriaPredictionConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
