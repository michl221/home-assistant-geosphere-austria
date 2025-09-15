"""Data model for GeoSphere Austria Prediction."""

from datetime import datetime

from pydantic import BaseModel


class Forecast(BaseModel):
    """GeoSphere Austria Prediction data model."""

    timestamps: list[datetime] | None
    global_radiation: list[float] | None
    minimum_temperature: list[float] | None
    maximum_temperature: list[float] | None
    rain_amount: list[float] | None
    relative_humidity: list[float] | None
    precipitation_amount: list[float] | None
    snow_amount: list[float] | None
    snow_limit: list[float] | None
    surface_pressure: list[float] | None
    sun_duration: list[float] | None
    symbol: list[float] | None
    temperature: list[float] | None
    total_cloud_cover: list[float] | None
    windspeed_eastward: list[float] | None
    windspeed_northward: list[float] | None
    ugust: list[float] | None
    vgust: list[float] | None
