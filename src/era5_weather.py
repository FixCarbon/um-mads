import datetime as dt
import io
import json
import logging
import os
from typing import Optional

import numpy as np
import pandas as pd
import requests
import xarray as xr

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

API_KEY = os.getenv("OIKOLAB_API_KEY")


class WeatherAPI:
    def __init__(self, polygon, timezone='UTC'):
        self.geometry = polygon
        self.timezone = timezone

    def get_data(
        self,
        start_date: Optional[str | dt.datetime] = pd.to_datetime("1985-01-01"),
        end_date: Optional[str | dt.datetime] = pd.to_datetime("2023-12-31"),
        frequency: str = "D",
        model="era5",
    ):
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)

        ds = self._get_area_data(start_date, end_date, frequency, model)
        return ds

    def _get_area_data(self, start_date, end_date, frequency, model):
        # TODO: Replace with your own way to get bounding box of your geometry
        bbox = self.geometry.bounds
        north = bbox[3]
        south = bbox[1]
        east = bbox[2]
        west = bbox[0]

        r = requests.get(
            "https://api.oikolab.com/weather",
            params={
                "param": "temperature",
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "north": north,
                "south": south,
                "east": east,
                "west": west,
                "api-key": API_KEY,
                "model": model,
                "format": "netcdf",
                "freq": frequency,
                "resample_method": "min"
            },
        )

        ncdf = r.content  # NetCDF is a single file format that is delivered as binary
        ds = xr.open_dataset(
            io.BytesIO(ncdf), engine="h5netcdf"
        )  # Open up the binary file
        ds.attrs["model"] = model

        # Note: The below is just to indicate how many API credits we are using
        x = max(int(ds["longitude"].max() - ds["longitude"].min()), 1)
        y = max(int(ds["latitude"].max() - ds["latitude"].min()), 1)
        # Get time in days
        time = max(
            int(
                (ds["time"].max() - ds["time"].min()) / np.timedelta64(1, "D") // 30.25
            ),
            1,
        )
        vars = len(ds.data_vars)
        data_units = int(x * y * time * vars) + 1

        logger.info(f"""Used {data_units} Oikolab units for query""")
        return ds