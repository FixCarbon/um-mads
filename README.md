# Climate Risks and Opportunities for Permanent Agriculture
Extensive research exists regarding the effects of climate change on agriculture. However, there is often a gap between researchers and decision makers, particularly in industries with limited resources. The apple industry is one such example. Though apples are the most consumed fruit in the United States, apple orchards occupy less than 1% of the 880 million acres of United States farmland (Industry at a Glance, n.d.; National Agricultural Statistics Service, 2024). To bridge this gap, we have developed a proof of concept for an apple manufacturer, providing insight into the resilience of cultivars in the Eastern Mountain region of the United States. Our findings suggest that this region will shift into the next USDA Plant Hardiness Zone within ten years, and that two apple cultivars—Cortland and Franklin Cider—may no longer be viable. If valuable, these insights could pave the way for other regions and crops, expanding both the accessibility and relevance of essential climate data.

## Getting Started
### Requirements
See the requirements.txt file in the requirements folder. GeoPandas, pandas, scikit-learn, and Xarray are used extensively.
### Installation
1. Clone the GitHub repository using `git clone https://github.com/FixCarbon/um-mads.git`.
2. Install dependencies using `pip install -r requirements/requirements.txt`.
3. Download a GeoTIFF file for a particular crop and region from `https://croplandcros.scinet.usda.gov/`.
4. Run the `create_polygons.ipynb` notebook with the GeoTIFF file to define a geographic area.
5. Run the `get_climate_data.ipynb` and `get_weather_data.ipynb` notebooks with the polygons from `create_polygons.ipynb` to retrieve data for the geographic area.
6. Run the `transform_data.ipynb` and `train_model.ipynb` notebooks to predict temperature and USDA Plant Hardiness Zone for the geographic area.
7. Run the `map_cultivars.ipynb` and `visualize_data.ipynb` notebooks create and save visuals.
## Requesting Data
To access climate data, users will need credentials for the FixCarbon Amazon S3 bucket. Similarly, to access weather data, users will need credentials for Oikolab. FixCarbon provided both sets of credentials for this project.
## Interpreting Results
Figures are within notebooks. Our model acheived an R2 score or 0.89, and predicted an increase in average hardiness zones from 6.5 to 8. However, most apple cultivars will still be able to be grown.

## References
* Hoplamazian, M. (2023, October 20). A bad apple season has some U.S. fruit growers planning for life in a warmer world. NPR. Retrieved April 17, 2024, from https://www.npr.org/2023/10/20/1207202139/a-bad-apple-season-has-some-u-s-fruit-growers-planning-for-life-in-a-warmer-worl
* Industry at a glance. (n.d.). USApple. Retrieved April 17, 2024, from https://usapple.org/industry-at-a-glance 
* Mohammed, I. N. (2024, January 13). Getting started with NEXGDDP-CMIP6 data. NASAaccess. Retrieved April 17, 2024, from https://imohamme.github.io/NASAaccess/articles/NEXGDDP-CMIP6.html 
* Morton, L. W., Cooley, D., Clements, J., & Gleason, M. (2017). Climate, weather and apples. Department of Sociology, Iowa State University. Retrieved April 17, 2024, from https://www.climatehubs.usda.gov/sites/default/files/Climate,%20Weather%20and%20Apples_0.pdf
* OpenAI. (2023). ChatGPT (January 16 version 4) [Large language model]. "Please annotate the following code and convert to PEP 8." https://chat.openai.com
* National Agricultural Statistics Service. (2024). Census of agriculture [Dataset]. United States Department of Agriculture. https://quickstats.nass.usda.gov/
* Peter, K. (2024). Penn State Tree Fruit Production Guide. The Pennsylvania State University.
* United States Department of Agriculture. (2023). 2023 USDA Plant Hardiness Zone Map. https://planthardiness.ars.usda.gov/system/files/National_Map_HZ_8x11_HS_300.png 
* Weber, C., J. Wechsler, S., & Wakefield, H. (2023). Fruit and Tree Nuts Yearbook [Dataset]. United States Department of Agriculture. https://www.ers.usda.gov/data-products/fruit-and-tree-nuts-data/fruit-and-tree-nuts-yearbook-tables/
