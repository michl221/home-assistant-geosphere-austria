"""DataUpdateCoordinator for the GeoSphere Austria Prediction integration."""

from __future__ import annotations

from datetime import UTC, datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE, CONF_ZONE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, SCAN_INTERVAL
from .geosphere_austria import GeoSphereAustriaError, GeoSphereAustriaPrediction
from .models import Forecast

type GeoSphereAustriaPredictionConfigEntry = ConfigEntry[
    GeoSphereAustriaPredictionUpdateCoordinator
]


class GeoSphereAustriaPredictionUpdateCoordinator(DataUpdateCoordinator[Forecast]):
    """A GeoSphere Austria Predictiona Data Update Coordinator."""

    config_entry: GeoSphereAustriaPredictionConfigEntry

    def __init__(
        self, hass: HomeAssistant, config_entry: GeoSphereAustriaPredictionConfigEntry
    ) -> None:
        """Initialize the GeoSphere Austria Prediction coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=f"{DOMAIN}_{config_entry.data[CONF_ZONE]}",
            update_interval=SCAN_INTERVAL,
        )
        session = async_get_clientsession(hass)
        self.geosphere_austria_prediction = GeoSphereAustriaPrediction(session=session)

    async def _async_update_data(self) -> Forecast:
        """Fetch data from GeoSphere Austria API."""
        if (zone := self.hass.states.get(self.config_entry.data[CONF_ZONE])) is None:
            raise UpdateFailed(f"Zone '{self.config_entry.data[CONF_ZONE]}' not found")

        try:
            latitude = zone.attributes[ATTR_LATITUDE]
            longitude = zone.attributes[ATTR_LONGITUDE]
            start = datetime.now(tz=UTC)
            return await self.geosphere_austria_prediction.query_geosphere_austria(
                latitude, longitude, start
            )
        except GeoSphereAustriaError as err:
            raise UpdateFailed("GeoSphere Austria API communication error") from err
