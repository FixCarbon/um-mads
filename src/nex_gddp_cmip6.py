import logging
import warnings
from typing import List

import xarray as xr

import geopandas
import rioxarray
from shapely.geometry import mapping

# Ignore warnings containing the substring "Performance"
warnings.filterwarnings("ignore", message=".*Increasing.*")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TIME_OPTIMIZED_ZARR_STORE_PATH = (
    "s3://cmip6-data/NEX-GDDP-CMIP6/NEX-GDDP-CMIP6-aoi-optimized"
)
TIME_OPTIMIZED_SCENARIOS = ["historical", "projection"]
AVAILABLE_SCENARIOS = ["historical", "ssp126", "ssp245", "ssp370", "ssp585"]
AVAILABLE_VARIABLES = [
    "hurs",
    "huss",
    "pr",
    "rlds",
    "rsds",
    "sfcWind",
    "tas",
    "tasmax",
    "tasmin",
]
CHUNKS = dict(lat=5, lon=5, model=1, scenario=4, time=31411)


def get_variable_groups(variables: List[str], scenarios: List[str]) -> List[str]:
    """Return a list of Zarr groups for the given variables and scenarios."""
    group_paths = [
        f"{TIME_OPTIMIZED_ZARR_STORE_PATH}/{scenario}/{variable}.zarr"
        for variable in variables
        for scenario in scenarios
    ]
    return group_paths


def preprocess_ds(ds: xr.Dataset) -> xr.Dataset:
    """Drop duplicate models from the dataset."""
    ds = ds.drop_duplicates("model", keep=False)

    # converts 0-360, circular to -180-+180  longitude
    ds = ds.assign_coords(lon=(((ds.lon + 180) % 360) - 180))
    ds = ds.roll(lon=int(len(ds['lon']) / 2), roll_coords=True)

    ds.attrs["crs"] = "EPSG:4326"
    return ds


def get_nex_dataset(variables: List[str], scenarios: List[str]) -> xr.Dataset:
    """Return an xarray Dataset for the given variables, models, and scenarios."""

    if not variables:
        raise ValueError("No variables provided.")
    if not scenarios:
        raise ValueError("No scenarios provided.")

    if set(variables).intersection(set(AVAILABLE_VARIABLES)) != set(variables):

        raise ValueError(
            f"One or more variables are not available: {set(variables) - set(AVAILABLE_VARIABLES)}"
        )
    if set(scenarios).intersection(set(TIME_OPTIMIZED_SCENARIOS)) != set(scenarios):
        raise ValueError(
            f"One or more scenarios are not available: {set(scenarios) - set(TIME_OPTIMIZED_SCENARIOS)}"
        )

    groups = get_variable_groups(variables, scenarios)
    ds = xr.open_mfdataset(
        groups, engine="zarr", consolidated=True, preprocess=preprocess_ds
    )
    return ds

def load_region(filepath):
    """Load a GeoJSON file into a GeoDataFrame and adjust longitude values.

    Args:
        filepath: Path to the GeoJSON file.

    Returns:
        A GeoDataFrame with adjusted longitude values.
    """
    geodataframe = geopandas.read_file(filepath)
    geodataframe.geometry = geodataframe.geometry.translate(xoff=180) # 360 converts -180 - 180 longitude to 0 - 360 longitude degrees east
    return geodataframe

def select_region(dataset, geodataframe):
    """Clip a dataset by a GeoDataFrame's boundaries.

    Args:
        dataset: The dataset to be clipped.
        geodataframe: A GeoDataFrame that defines the region to clip.

    Returns:
        The clipped dataset.
    """

    # https://corteva.github.io/rioxarray/html/getting_started/crs_management.html
    rio_dataset = dataset.rio.write_crs("EPSG:4326").rio.set_spatial_dims('lon', 'lat', inplace = True)
    return rio_dataset.rio.clip(geodataframe.geometry.apply(mapping), geodataframe.crs)