"""Common fixtures for the GeoSphere Austria Prediction tests."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_ZONE
from pytest_homeassistant_custom_component.common import (MockConfigEntry,
                                                          load_fixture)
from pytest_homeassistant_custom_component.syrupy import \
    HomeAssistantSnapshotExtension

from custom_components.geosphere_austria_prediction.const import DOMAIN
from custom_components.geosphere_austria_prediction.models import Forecast

# from syrupy.assertion import SnapshotAssertion




# @pytest.fixture
# def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
#     """Return snapshot assertion fixture with the Home Assistant extension."""
#     return snapshot.use_extension(HomeAssistantSnapshotExtension)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations."""
    yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return the default mocked config entry."""
    return MockConfigEntry(
        title="Home",
        domain=DOMAIN,
        data={CONF_ZONE: "zone.home"},
        unique_id="zone.home",
    )


@pytest.fixture
def mock_setup_entry() -> Generator[None]:
    """Override async_setup_entry."""
    with patch(
        "custom_components.geosphere_austria_prediction.async_setup_entry",
        return_value=True,
    ):
        yield


@pytest.fixture
def mock_geosphere_austria_prediction(
    request: pytest.FixtureRequest,
) -> Generator[MagicMock]:
    """Return a mocked GeoSphere Austria client."""
    fixture: str = "forecast.json"
    if hasattr(request, "param") and request.param:
        fixture = request.param

    forecast = Forecast.model_validate_json(load_fixture(fixture))
    with patch(
        "custom_components.geosphere_austria_prediction.coordinator.GeoSphereAustriaPrediction",
        autospec=True,
    ) as geosphare_austria_prediction_mock:
        geosphere_austria_prediction = geosphare_austria_prediction_mock.return_value
        geosphere_austria_prediction.query_geosphere_austria.return_value = forecast
        yield geosphere_austria_prediction
