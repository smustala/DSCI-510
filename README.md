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

This is a snippet of the final data:
![Alt text](data_snippet.png?raw=true "Title")

## Analysis:
The correlation coefficients (below) between the variables show that the death rates due to ambient air pollution increase with the Air Quality Index (which is the inverse of goodness of air quality). But it seems to be decreasing with population density and increasing with GDP which is unexpected. In order to study the relationships better, I’ve used an ordinary least squares regression with death rate as the dependent variable, GDP, avg_aqi and population density as independent variables. 

From the regression results, it has ben found that GDP has a negative coefficient and a p-value of 0.079 suggesting statistical significance of the relationship between GDP and death rates at 10% confidence level. The p-value of the interaction term between GDP and air quality index is 0.045 suggesting statistical significance at 5% confidence level. It is also worth noting that the R-squared value of this regression is quite low, suggesting low explanatory power of the variables.

The below chart attempts to show this interaction effect of GDP and Air Quality Index on the death rates. We can see that on average, for a group of countries having the same AQI, the death rate increases with decreasing GDP. That means, the effects of bad air quality are worse in poorer countries when compared to countries with higher GDP.
![Alt text](Chart1.png?raw=true "Title")

The below graph shows the relationship between death rates due all the three country level characteristics (air quality, GDP and population density) of the top 50 countries sorted by GDP. The colors of the bubbles depict avg_aqi and sizes depict population density. It can be seen that countries with similar GDPs usually have higher AQI (poorer air quality) with increasing population density.
![Alt text](Chart2.png?raw=true "Title")

## Conclusions:
1. The data shows that the effect of air pollution in terms of death rate is worse in countries with low GDP when compared to countries with high GDP.
2. Countries with similar levels of GDP have poorer air quality with increasing population density
3. Ordinary Least Squares on the data shows statistically significant relationship of the interaction between GDP and air quality on the death rate.

## Further Research
A low R-squared value is observed. This shows the low explanatory power of the variables. And could possibly mean that other factors like quality and accessibility of healthcare and measures to curb the effects of air pollution also play an important role in determining deaths due to bad air quality. Therefore, further research to collect and analyze healthcare and environmental data could result in better understanding of the effects of air pollution.
