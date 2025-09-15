"""Test for the GeoSphere Austria Prediction weather entity."""

from unittest.mock import AsyncMock

import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.weather import (
    DOMAIN as WEATHER_DOMAIN,
    SERVICE_GET_FORECASTS,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry


@pytest.mark.freeze_time("2025-09-15T15:00:00Z")
async def test_forecast_service(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_geosphere_austria_prediction: AsyncMock,
    snapshot: SnapshotAssertion,
) -> None:
    """Test forecast service."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    response = await hass.services.async_call(
        WEATHER_DOMAIN,
        SERVICE_GET_FORECASTS,
        {ATTR_ENTITY_ID: "weather.home", "type": "hourly"},
        blocking=True,
        return_response=True,
    )
    assert response == snapshot(name="forecast_hourly")
