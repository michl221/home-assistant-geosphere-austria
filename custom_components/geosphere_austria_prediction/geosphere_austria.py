"""GeoSphere Austria Prediction API wrapper."""

import asyncio
from dataclasses import dataclass
import datetime
import socket
import json

import aiohttp
from aiohttp.client import ClientError, ClientResponseError, ClientSession

from .const import LOGGER
from .models import Forecast

nwp_api_url = (
    "https://dataset.api.hub.geosphere.at/v1/timeseries/forecast/nwp-v1-1h-2500m"
)

nwp_forecast_params = {
    "lat_lon": None,
    "parameters": [
        "grad",
        "mnt2m",
        "mxt2m",
        "rain_acc",
        "rh2m",
        "rr_acc",
        "snow_acc",
        "snowlmt",
        "sp",
        "sundur_acc",
        "sy",
        "t2m",
        "tcc",
        "u10m",
        "ugust",
        "v10m",
        "vgust",
    ],
    "start": None,
    "end": None,
    "output_format": "geojson",
}


@dataclass
class GeoSphereAustriaPrediction:
    """Main class to access the GeoSphere Austria Weather Prediction API (NWP)."""

    # Request timeout in seconds.
    request_timeout: float = 10.0

    # Custom client session to use for requests.
    session: ClientSession | None = None

    _close_session: bool = False

    async def query_geosphere_austria(self, latitude, longitude, start) -> Forecast:
        """Queries the API of GeoSphere Austria numerical weather prediction."""
        nwp_forecast_params["lat_lon"] = f"{latitude},{longitude}"
        nwp_forecast_params["start"] = str(start)
        nwp_forecast_params["end"] = str(start + datetime.timedelta(hours=90))
        if self.session is None:
            self.session = aiohttp.client.ClientSession()
            self._close_session = True

        try:
            LOGGER.info(f"GeoSphereAustriaPrediction {nwp_forecast_params}")
            async with asyncio.timeout(delay=None):
                response = await self.session.get(
                    url=nwp_api_url, params=nwp_forecast_params
                )
        except TimeoutError as exception:
            msg = "Timeout while requesting forecast from GeoSphere Austria"
            raise GeoSphereAustriaConnectionError(msg) from exception
        except (ClientError, ClientResponseError, socket.gaierror) as exception:
            msg = "Error occured while communicating with GeoSphere Austria API"
            raise GeoSphereAustriaConnectionError(msg) from exception

        LOGGER.info(f"GeoSphereAustriaPrediction {response.status}")
        if response.status in (200, 301):
            json_contents = await response.json()

        if self._close_session:
            await self.session.close()

        if json_contents:
            with open("forecast.json", "wt") as of:
                json.dump(json_contents, of)
            response.close()
            predictions = json_contents["features"][0]["properties"]["parameters"]
            LOGGER.info(f"{json_contents['timestamps']}")
            timestamps = [
                datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M%z")
                for x in json_contents["timestamps"]
            ]
            grad = predictions["grad"]["data"]
            mnt2m = predictions["mnt2m"]["data"]
            mxt2m = predictions["mxt2m"]["data"]
            rain_acc = predictions["rain_acc"]["data"]
            rh2m = predictions["rh2m"]["data"]
            rr_acc = predictions["rr_acc"]["data"]
            snow_acc = predictions["snow_acc"]["data"]
            snowlmt = predictions["snowlmt"]["data"]
            sp = predictions["sp"]["data"]
            sundur_acc = predictions["sundur_acc"]["data"]
            sy = predictions["sy"]["data"]
            t2m = predictions["t2m"]["data"]
            tcc = predictions["tcc"]["data"]
            u10m = predictions["u10m"]["data"]
            ugust = predictions["ugust"]["data"]
            v10m = predictions["v10m"]["data"]
            vgust = predictions["vgust"]["data"]

            data = Forecast(
                timestamps=timestamps,
                global_radiation=grad,
                minimum_temperature=mnt2m,
                maximum_temperature=mxt2m,
                rain_amount=rain_acc,
                relative_humidity=rh2m,
                precipitation_amount=rr_acc,
                snow_amount=snow_acc,
                snow_limit=snowlmt,
                surface_pressure=sp,
                sun_duration=sundur_acc,
                symbol=sy,
                temperature=t2m,
                total_cloud_cover=tcc,
                windspeed_eastward=u10m,
                windspeed_northward=v10m,
                ugust=ugust,
                vgust=vgust,
            )
            LOGGER.info(f"Forecast {data}")
            with open("forecast_model.json", "wt") as of:
                of.write(data.model_dump_json())
            return data
        return None


class GeoSphereAustriaError(Exception):
    """GeoSphere Austria exception."""


class GeoSphereAustriaConnectionError(GeoSphereAustriaError):
    """GeoSphere Austria connection exception."""
