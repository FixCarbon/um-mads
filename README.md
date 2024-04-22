# Climate Risks and Opportunities for Permanent Agriculture
Extensive information exists regarding the effects of climate change on agriculture. However, there is often a gap between the individuals responsible for publishing this information and the individuals responsible for making decisions. This gap is particularly acute for permanent crops, such as apples. To bridge this gap, we have developed a proof of concept for apple growers and apple processors, providing insight into the cultivars that will and will not be resilient in face of climate change, focusing on the next twenty years for existing orchards in the Eastern Mountain region of the United States. If successful, a similar approach could be used in other regions, for other decisions, or for other permanent crops, democratizing the availability of climate data.

## Getting Started
### Requirements
See requirements.txt in requirements folder. Geopandas, pandas and xarray are used heavily.
### Installation
1. Clone repository with git clone https://github.com/FixCarbon/um-mads.git
2. Install dependencies with pip install -r requirements/requirements.txt
3. create_polygons.ipynb, scrape_cultivars.ipynb, get_climate_data.ipynb, and get_weather_data.ipynb specify and pull the selected data.
4. transform_data.ipynb and train_model.ipynb reshape and run predictions on the selected data.
5. map_cultivars.ipynb and visualize_data.ipynb create and save visuals from model results.
## Requesting Data
Climate model and climate data came from APIs by Fix6 and Oikolab, in the NEX-GDDP-CMIP6 downscaled daily predictions and the ERA5 datasets respectively, which require their own access keys.
## Interpreting Results
Figures are within notebooks. Our model acheived an R2 score or 0.89, and predicted an increase in average hardiness zones from 6.5 to 8. However, most apple cultivars will still be able to be grown.