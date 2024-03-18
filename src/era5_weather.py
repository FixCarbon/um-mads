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

PARAMS = dict(
    temperature=["mean", "min", "max"],
    dewpoint_temperature=["mean"],
    wind_speed=["mean", "max"],
    surface_pressure=["mean"],
    surface_solar_radiation=["sum"],
    surface_thermal_radiation=["sum"],
    surface_net_solar_radiation=["sum"],
    surface_direct_solar_radiation=["sum"],
    surface_diffuse_solar_radiation=["sum"],
    total_cloud_cover=["mean"],
    total_precipitation=["sum"],
    relative_humidity=["mean"],
)

SNOW_PARAMS = dict(
    snowfall=["sum"],
    snow_depth=["max"],
)

COLUMN_MAPPING = dict(
    temperature="temperature_degC",
    dewpoint_temperature="dewpoint_temperature_degC",
    wind_speed="wind_speed_m_per_s",
    surface_pressure="surface_pressure_Pa",
    surface_solar_radiation="surface_solar_radiation_W_per_m2",
    surface_thermal_radiation="surface_thermal_radiation_W_per_m2",
    surface_net_solar_radiation="total_solar_radiation",  # Assumed mapping
    total_precipitation="total_precipitation_mm_of_water_equivalent",
    relative_humidity="relative_humidity_0_1",
)


def clean_column_names(df):
    new_columns = []

    # Iterate over each column name
    for col in df.columns:
        # Replace specific characters with words or remove them
        cleaned_name = col.replace("/", " per ").replace("^", "")

        # Keep only the characters that are alphanumeric or underscore
        cleaned_name = "".join(
            c if c.isalnum() or c == "_" else " " for c in cleaned_name
        )

        # Replace spaces with underscores
        cleaned_name = "_".join(cleaned_name.split())

        # Append the cleaned name to the new_columns list
        new_columns.append(cleaned_name)

    # Assign the new column names to the DataFrame
    df.columns = new_columns
    return df


def get_weather_data_df(response) -> pd.DataFrame:
    logger.info(
        f"""Used {response["attributes"]["n_parameter_months"]} Oikolab units for query"""
    )
    weather_data = json.loads(response["data"])
    df = pd.DataFrame(
        index=pd.to_datetime(weather_data["index"], unit="s"),
        data=weather_data["data"],
        columns=weather_data["columns"],
    )
    return df


class WeatherAPI:
    def __init__(self, gs, local_tz = 'UTC'):
        # TODO: We use "project_id" as a primitive that can be used to fetch a ton of information
        # about a projectm, which represents some geographic area. What you'll want to do is replace
        # this with some variable that contains the geographical area of interest: done
        
        # gs = GeoPandas.GeoSeries
        self.geometry = gs
        self.local_tz = local_tz

        if 'polygon' in str(type(gs.iloc[-1])):
            self.is_polygon = True
        else:
            self.is_polygon = None


    def get_data(
        self,
        start_date: Optional[str | dt.datetime] = pd.to_datetime("2015-01-01"),
        end_date: Optional[str | dt.datetime] = dt.datetime.utcnow(),
        frequency: str = "hourly",
        model="era5",
    ):
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)

        # TODO: Replace these if statements with something that matches your geometry variables: done
        if self.is_polygon:  # For projects with mutliple geometries, get NetCDF
            ds = self._get_area_data(start_date, end_date, frequency, model)
            return ds
        else:  # If just point data
            df = self._get_location_data(start_date, end_date, frequency, model)
            return df

    def _get_area_data(self, start_date, end_date, frequency, model):

        # TODO: done
        bbox = self.geometry.unary_union.bounds
        # Add a 10% buffer to the bounding box
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        bbox = (
            bbox[0] - 0.1 * width,
            bbox[1] - 0.1 * height,
            bbox[2] + 0.1 * width,
            bbox[3] + 0.1 * height,
        )
        north = bbox[3]
        south = bbox[1]
        east = bbox[2]
        west = bbox[0]

        r = requests.get(
            "https://api.oikolab.com/weather",
            params={
                "param": PARAMS.keys(),
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "north": north,
                "south": south,
                "east": east,
                "west": west,
                "api-key": API_KEY,
                "model": model,
                "format": "netcdf",
                "frequency": frequency,
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

    def _get_location_data(self, start_date, end_date, frequency, model):
        # TODO: Replace with your own way to get lat/lon of your geometry: done

        # lat: a list of latitudes
        # lon a list of longitudes        
        lat, lon = self.geometry.centroid.y.values, self.geometry.centroid.x.values

        if (np.abs(lat) > 35).any():
            for param in SNOW_PARAMS:
                PARAMS[param] = SNOW_PARAMS[param]
        # API Reference: https://docs.oikolab.com/references/#weather

        r = requests.get(
            "https://api.oikolab.com/weather",
            params={
                "param": PARAMS.keys(),
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "lat": lat,
                "lon": lon,
                "api-key": API_KEY,
                "model": model,
            },
        )
        response = r.json()
        df = get_weather_data_df(response)
        return df

    def _create_dataframe(self, data):
        if isinstance(data, xr.Dataset):
            df = data.to_dataframe()
            df = df.reset_index()
            df = clean_column_names(df)
            df = df.rename(
                columns=dict(time="timestamp_utc", longitude="lon", latitude="lat")
            )
            # Need to make explicit renaming of column names because NetCDF delivers
            # different variable names than JSON
            df = df.rename(columns=COLUMN_MAPPING)
            df["model"] = data.attrs["model"]
        elif isinstance(data, pd.DataFrame):
            df = data.reset_index()
            df = df.rename(columns=dict(index="timestamp_utc", model_name="model"))
            df = clean_column_names(df)
            df[["lat", "lon"]] = df["coordinates_lat_lon"].str.extract(
                r"\((.*), (.*)\)"
            )
        else:
            raise ValueError(f"Data type {type(data)}not supported")

        df["timestamp_utc"] = df["timestamp_utc"].dt.tz_localize("UTC")
        # Use the `utc_offset_hrs` column to convert timezone
        # TODO: figure out a way to get the timezone for the area that you're looking at: done
        # https://www.w3resource.com/pandas/series/series-dt-tz_convert.php#:~:text=dt.-,tz_convert()%20function,one%20time%20zone%20to%20another.&text=Time%20zone%20for%20time.
        df["timestamp_local"] = df["timestamp_utc"].dt.tz_convert(self.local_tz)

        df["lat"] = df["lat"].astype(float)
        df["lon"] = df["lon"].astype(float)

        for col in [
            "snowfall_mm_of_water_equivalent",
            "snow_depth_mm_of_water_equivalent",
        ]:
            if col not in df.columns:
                df[col] = None

        return df
