# Course Project - DSCI 510
## Motivation:
This project aims to study the effects of air pollution on different countries by looking at the deaths due to acute respiratory diseases caused by polluted air. The purpose of this project is to understand what factors contribute to higher death rates due to air pollution.

## Data Sources
1. Scraping Wikipedia The wiki page
https://en.wikipedia.org/wiki/List_of_countries_by_largest_and_second_largest_cities
has been scraped to get a list of links of wikipedia pages of each country and links of each country’s two largest cities. This list of country urls has been further scraped to get GDP and population density of each country. The list of city urls are scraped to extract the geographical coordinates of each city.
The wiki page https://en.wikipedia.org/wiki/List_of_alternative_country_names is scraped to get the “Alpha-3-codes” of all the countries. These codes are unique alternative names for the countries. These codes are used to merge the data with mortality data from WHO.
2. OpenWeather API
The openweather air pollution API (https://openweathermap.org/api/air-pollution) is used to request air pollution index for each of the major cities whose latitudes and longitudes are stored as a csv after scraping the wikipedia pages. Air quality index given by the API ranges on a scale 1 to 5. (1: Good, 2: Fair, 3: Moderate, 4: Poor, 5: Very Poor)
3. WHO
The mortality data for the number of deaths occurring in each country due to ambient air pollution for the year 2016 has been collected using the downloadable csv in WHO webpage https://www.who.int/data/gho/data/indicators/indicator-details/GHO/ambient-air-pollutio n-attributable-deaths

## Data Cleaning:
The merged data has been cleaned by removing missing data, converting the air quality data and population density into required data types. The air quality indices of two largest cities of each country are averaged into “avg_aqi”. This is used as a proxy for the overall air quality of the country. The countries are further divided into groups of GDP : Low, Mid and High. "Low" consists of countries falling below 25 percentile, "Medium" consists of countries falling between 25 and 75 percentile, and "High" consists of countries falling above 75 percentile.

![Alt text](data_snippet.png?raw=true "Title")
