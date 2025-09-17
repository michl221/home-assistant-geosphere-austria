"""Support for GeoSphere Austria Prediction."""

from __future__ import annotations

from datetime import datetime, time
import math

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_PRECIPITATION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_PRESSURE,
    Forecast,
    SingleCoordinatorWeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.const import (
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import DOMAIN, GSA_TO_HA_CONDITION_MAP, LOGGER
from .coordinator import GeoSphereAustriaPredictionConfigEntry
from .models import Forecast as GeoSphereAustriaForecast


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GeoSphereAustriaPredictionConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up GeoSphere Austria Prediction weather entity based on config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        [GeoSphereAustriaPredictionWeatherEntity(entry=entry, coordinator=coordinator)]
    )


class GeoSphereAustriaPredictionWeatherEntity(
    SingleCoordinatorWeatherEntity[DataUpdateCoordinator[GeoSphereAustriaForecast]]
):
    """Defines GeoSphere Austria weather entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND
    _attr_supported_features = WeatherEntityFeature.FORECAST_HOURLY
    _attr_native_pressure_unit = UnitOfPressure.HPA

    def __init__(
        self,
        *,
        entry: GeoSphereAustriaPredictionConfigEntry,
        coordinator: DataUpdateCoordinator[GeoSphereAustriaForecast],
    ) -> None:
        """Initialize GeoSphereAustria Prediction weather entity."""
        super().__init__(coordinator=coordinator)
        self._attr_unique_id = entry.entry_id

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="GeoSphere Austria",
            name=entry.title,
        )

    @property
    def condition(self) -> str | None:
        """Return the current weather condition."""
        if not self.coordinator.data.symbol:
            return None
        return GSA_TO_HA_CONDITION_MAP[self.coordinator.data.symbol[0]]

    @property
    def native_temperature(self) -> float | None:
        """Return the platform temperature."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.temperature[0]

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        if (
            not self.coordinator.data.windspeed_eastward
            or not self.coordinator.data.windspeed_northward
        ):
            return None
        return math.sqrt(
            math.pow(self.coordinator.data.windspeed_eastward[0], 2)
            + math.pow(self.coordinator.data.windspeed_northward[0], 2)
        )

    @property
    def native_pressure(self) -> float | None:
        """Return the surface presssure."""
        if not self.coordinator.data.surface_pressure:
            return None
        return self.coordinator.data.surface_pressure[0] / 100

    # @property
    # def wind_bearing(self) -> float | str | None:
    #     """Return the wind bearing."""
    #     if not self.coordinator.data.current_weather:
    #         return None
    #     return self.coordinator.data.current_weather.wind_direction

    @callback
    def _async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the daily forecast in native units."""

        if self.coordinator.data is None:
            return None

        forecasts: list[Forecast] = []

        today = dt_util.utcnow()

        hourly = self.coordinator.data
        for index, _datetime in enumerate(hourly.timestamps):
            if _datetime.tzinfo is None:
                _datetime = _datetime.replace(tzinfo=dt_util.UTC)
            if _datetime < today:
                continue

            forecast = Forecast(
                datetime=_datetime.isoformat(),
            )

            if hourly.temperature is not None:
                forecast[ATTR_FORECAST_NATIVE_TEMP] = hourly.temperature[index]
            if hourly.symbol is not None:
                forecast[ATTR_FORECAST_CONDITION] = GSA_TO_HA_CONDITION_MAP.get(
                    hourly.symbol[index]
                )

            if hourly.precipitation_amount is not None:
                forecast[ATTR_FORECAST_NATIVE_PRECIPITATION] = (
                    hourly.precipitation_amount[index]
                )
            if hourly.minimum_temperature is not None:
                forecast[ATTR_FORECAST_NATIVE_TEMP_LOW] = hourly.minimum_temperature[
                    index
                ]

            if (
                hourly.windspeed_eastward is not None
                and hourly.windspeed_northward is not None
            ):
                forecast[ATTR_FORECAST_NATIVE_WIND_SPEED] = math.sqrt(
                    math.pow(hourly.windspeed_eastward[index], 2)
                    + math.pow(hourly.windspeed_northward[index], 2)
                )
            if hourly.surface_pressure is not None:
                forecast[ATTR_FORECAST_PRESSURE] = hourly.surface_pressure[index] / 100

            forecasts.append(forecast)

        return forecasts
