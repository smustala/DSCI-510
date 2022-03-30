#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 11:40:26 2021

@author: shalinimustala
"""
import ast
from statsmodels.formula.api import ols
import seaborn as sns
import matplotlib.pyplot as plt
import json
import math
import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
from requests.exceptions import HTTPError
import requests
import numpy as np
import pandas as pd
import sys
import warnings
warnings.filterwarnings("ignore")
import glog as log

#import statsmodels.api as sm


# Web Scraping - Wikipedia

#This function parses the content of a webpage
def getContent(link):
    # get HTML Content
    url = urlopen(link)
    soup = BeautifulSoup(url, 'html.parser')
    return soup

# This function extracts population density of each country from the country's wiki page
# The urls for each country is taken from the countries dataframe
def PopDensity(url):
    try:
        country_page = getContent('https://en.wikipedia.org' + url)
        log.info("Now working with " + url)
        table = country_page.find('table', {'class': 'infobox'})
        additional_details = []
        for tr in table.find_all('tr'):
            if tr.find('div') is not None:
                if tr.get('class') == ['mergedbottomrow'] and "Density" in tr.find(
                        'div').get_text().strip():
                    additional_details.append(
                        tr.find('td').get_text().strip('\n').split(" ")[0])
        return additional_details
    except Exception as err:
        log.error("Error occured: {}".format(err))
        return []

# This function extracts GDPs of the countries
def getGDP(url_GDP):
    content = getContent(url_GDP)
    # The table "wikitable sortable static-row-numbers plainrowheaders
    # srn-white-background" has the required info
    table = content.find('table',
                         {'class': ['wikitable',
                                    'sortable',
                                    'static-row-numbers',
                                    'plainrowheaders',
                                    'srn-white-background']})
    rows = table.find_all('tr')
    # Make a dict of country names as keys and GDPs as values
    gdp_dict = {}
    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 2:
            # The first row contains the name and link of the countries
            country = cells[0].find('a')
            if country is not None:
                country_name = country.get_text()
                # The thrid row contains GDP in million dollars
                gdp = cells[4].get_text()
                gdp_dict[country_name] = gdp
    return gdp_dict

# This function extracts Lat, Long for major cities in each country
def getgeo(city_url):
    try:
        content = getContent("https://en.wikipedia.org" + city_url)
        # The table of interest has class name "infobox"
        table = content.find('table', {'class': 'infobox'})
        # print(table.prettify())
        if table is not None:
            rows = table.find_all('tr')
            for tr in rows:
                # Longitude
                if tr.find("td") is not None and tr.find("td").find(
                        "span", {"class": "longitude"}) is not None:
                    long = tr.find("td").find(
                        "span", {"class": "longitude"}).get_text()
                # Latitude
                if tr.find("td") is not None and tr.find("td").find(
                        "span", {"class": "latitude"}) is not None:
                    lat = tr.find("td").find(
                        "span", {"class": "latitude"}).get_text()
                    log.info("Done " + city_url)
                    return [lat, long]

    except Exception as err:
        log.error('Error occured: {}'.format(err))
        return np.NaN
        
# Convert coordinates to float (in order to match the OpenWeatherMap's API)
# This part of the code is modified from the code found in the reference mentioned
# Reference:
# https://en.proft.me/2015/09/20/converting-latitude-and-longitude-decimal-values-p/
def dms2dd(*args):
    # Initialize with zeros
    degrees = 0
    minutes = 0
    seconds = 0
    degrees = args[0]
    if len(args) < 3:  # has only degrees and direction
        direction = args[1]
    elif len(args) < 4:  # has deg, min and direction
        minutes = args[1]
        direction = args[2]
    else:  # has deg, min, sec and direction
        minutes = args[1]
        seconds = args[2]
        direction = args[3]

    dd = float(degrees) + float(minutes) / 60 + float(seconds) / (60 * 60)
    if direction == 'S' or direction == 'W':
        dd *= -1
    return dd

# Convert Coordinates to Float
def parse_dms(dms):
    if isinstance(dms, list):
        # Latitude
        # print(dms)
        parts_lat = re.split('[^\\d\\w]+', dms[0])
        if len(parts_lat) < 3:
            lat = dms2dd(parts_lat[0], parts_lat[1])
        elif len(parts_lat) < 4:
            lat = dms2dd(parts_lat[0], parts_lat[1], parts_lat[2])
        else:
            lat = dms2dd(
                parts_lat[0],
                parts_lat[1],
                parts_lat[2],
                parts_lat[3])
        # Longitude
        parts_long = re.split('[^\\d\\w]+', dms[1])
        if len(parts_long) < 3:
            lng = dms2dd(parts_long[0], parts_long[1])
        elif len(parts_long) < 4:
            lng = dms2dd(parts_long[0], parts_long[1], parts_long[2])
        else:
            lng = dms2dd(
                parts_long[0],
                parts_long[1],
                parts_long[2],
                parts_long[3])

        return ([round(lat, 3), round(lng, 3)])
    else:
        return np.NaN

# This function requests the OpenWeatherMap API for Air Quality Data
def pollution(coordinates):
    if isinstance(coordinates, list):
        lat = float(coordinates[0])
        long = float(coordinates[1])
        url = "http://api.openweathermap.org/data/2.5/air_pollution?lat={}&lon={}&APPID=dbc27700b3404b33e9e1e1663e722bbb".format(
            lat, long)
        res = requests.get(url)
        res_dict = json.loads(res.text)
        return [res_dict["list"][0]["components"], res_dict["list"][0]["main"]]
    elif isinstance(coordinates, str):
        latlong = coordinates.strip('][').split(',')
        lat = float(latlong[0])
        long = float(latlong[1])
        url = "http://api.openweathermap.org/data/2.5/air_pollution?lat={}&lon={}&APPID=dbc27700b3404b33e9e1e1663e722bbb".format(
            lat, long)
        res = requests.get(url)
        res_dict = json.loads(res.text)
        return [res_dict["list"][0]["components"], res_dict["list"][0]["main"]]

    else:
        return coordinates
        
# This function gets the average of air quality indices of the two largest cities of each 
# country.
# This avg_aqi is considered as proxy for the overall air quality index of the country
def avg_aqi(row):
    if not isinstance(row["city2_air_quality"], list):
        avg_aqi = row["city1_air_quality"][1]["aqi"]
    elif not isinstance(row["city1_air_quality"], list):
        avg_aqi = row["city2_air_quality"][1]["aqi"]
    else:
        avg_aqi = (row["city1_air_quality"][1]["aqi"] +
                   row["city2_air_quality"][1]["aqi"]) / 2
    return avg_aqi

#This function extracts data from multiple sources, cleans and merges them 
def default_function():

    # Get Country Codes for each country for comparability accross datasets
    url = "https://en.wikipedia.org/wiki/List_of_alternative_country_names"
    content = getContent(url)
    codes_dict = {}
    for table in content.find_all('table', {"class": "wikitable"}):
        for row in table.find_all("tr"):
            cells = row.find_all('td')
            if len(cells) > 1:
                country_code = cells[0].get_text().strip()
                country_name = cells[1].find("a").get_text().strip()
                codes_dict[country_name] = country_code
    codes = pd.DataFrame.from_dict(codes_dict, orient='index').reset_index()
    codes.columns = ["Country Name", "Country Code"]

    # Using the wiki page for list of countries and major cities
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_largest_and_second_largest_cities"
    content = getContent(url)
    # The table "wikitable sortable" has the required info
    table = content.find('table', {'class': 'wikitable sortable'})
    rows = table.find_all('tr')
    # List of all links
    # Make a dict of country names as keys and values being a list of 3 links:
    # [link of the country's wiki page, link of it's largest cuty, link of
    # second largest city]
    country_dict = {}
    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 2:
            country = cells[0].find('a')  # This cell has country name
            city1 = cells[1].find('a')  # This cell has the largest city
            city2 = cells[2].find('a')  # This cell has the second largest city
            if country is not None:
                country_name = country.get('href').split("/")[-1]
                country_link = country.get('href')
                if city1 is not None:
                    largestcity_link = city1.get('href')
                if city2 is not None:
                    secondcity_link = city2.get('href')
                country_dict[country_name] = [
                    country_link, largestcity_link, secondcity_link]
    # Make a dataframe from the dictionary
    countries = pd.DataFrame.from_dict(country_dict, orient='index')
    countries.reset_index(inplace=True)
    countries.columns = [
        "Country Name",
        "Country Link",
        "City1 Link",
        "City2 Link"]
    # Removing "_" from the country names
    countries["Country Name"] = countries["Country Name"].apply(
        lambda x: x.replace("_", " "))
    # Extracting the names of cities
    countries["City1"] = countries["City1 Link"].apply(
        lambda x: x.split("/")[-1])
    countries["City2"] = countries["City2 Link"].apply(
        lambda x: x.split("/")[-1])
    # Merge with country codes
    countries = pd.merge(codes, countries, on="Country Name", how="outer")
    # Population Density
    countries["Population Density"] = countries["Country Link"].apply(
        PopDensity)
    # Converting Population Density to a string object
    countries["Population Density"] = countries["Population Density"].apply(
        lambda x: x[0] if len(x) > 0 else np.nan)

    # Extracting GDPs
    # GDPs of all the countries can be found in this Wikipedia page:
    # https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)
    url_GDP = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    gdp_dict = getGDP(url_GDP)
    gdp = pd.DataFrame.from_dict(gdp_dict, orient='index').reset_index()
    gdp.columns = ["Country Name", "GDP"]
    # Convert GDPs to float
    gdp["GDP"] = gdp["GDP"].apply(
        lambda x: float(
            x.replace(
                ",",
                "")) if x[0].isdigit() else np.nan)
    country_gdp = pd.merge(countries, gdp, on="Country Name", how="inner")
    # Get Lat, Long for major cities in each country
    country_gdp["city1_coordinates"] = country_gdp["City1 Link"].apply(getgeo)
    country_gdp["city2_coordinates"] = country_gdp["City2 Link"].apply(getgeo)
    # Converting Coordinates to float
    country_gdp["city1_coordinates"] = country_gdp["city1_coordinates"].apply(
        parse_dms)
    country_gdp["city2_coordinates"] = country_gdp["city2_coordinates"].apply(
        parse_dms)
    country_gdp["city1_air_quality"] = country_gdp["city1_coordinates"].apply(
        pollution)
    country_gdp["city2_air_quality"] = country_gdp["city2_coordinates"].apply(
        pollution)

    # Reading data from a downloaded dataset from WHO (3rd dataset)
    who_data = pd.read_csv("who-data-downloaded.csv")
    # Each country has multiple rows of data for death rate for different genders and 
    #different health conditions
    # The column Dim1 has sex and column Dim2 has the reason of death
    # We need "Total" number of deaths per 100,000 people averaged over all the sexes.
    # FactValueNumeric has the value for number of deaths per 100,000 people
    data_grouped = who_data[who_data["Dim2"] == "Total"].groupby(
        "SpatialDimValueCode")["FactValueNumeric"].mean().reset_index()
    data_grouped.columns = ["Country Code", "Death rate"]
    # Merge it with countries and airquality data
    data = pd.merge(country_gdp, data_grouped, on="Country Code", how="inner")

    # Analysis Starts Here
    # Drop the rows that have no air quality or deaths information
    # Drop rows that don't have air quality info in either cities
    data.dropna(
        axis=0,
        how='all',
        subset=[
            "city1_air_quality",
            "city2_air_quality"],
        inplace=True)
    # Drop rows that don't have death rate information
    data.dropna(axis=0, subset=["Death rate"], inplace=True)
    data["avg_aqi"] = data.apply(avg_aqi, axis=1)
    # Converting Population Density to numeric datatype
    data["Population Density"] = data["Population Density"].apply(lambda x: float(
        x.split("/")[0].replace(",", "").split("[")[0]) if isinstance(x, str) else x)
    # Retaining only relevant columns for analysis
    data = data[['Country Name', 'Population Density',
                 'GDP', 'Death rate', 'avg_aqi']]
    # Print the correlation table
    print("Correlations in the data:")
    print(data.corr())
    data = data.sort_values(by="GDP", axis=0, ascending=False)
    data.rename(
        columns={
            "Death rate": "Death_rate",
            "Population Density": "Pop_Density"},
        inplace=True)

    # OLS
    model = ols(
        "Death_rate ~ avg_aqi + GDP + Pop_Density + GDP*avg_aqi",
        data=data).fit()
    # View model summary
    print("Summary of the ordinary least squares model with death rate as dependent \
    	variable, GDP, population density and air quality as independent variables:")
    print("\n")
    print(model.summary())

    # Charts
    
    # Categorize the GDPs into groups.
    # "Low" consists of countries falling below 25 percentile, "Medium" consists of 
    #countries falling between 25 and 75 percentile, and "High" consists of countries 
    #falling above 75 percentile
    bins = [
        data["GDP"].describe()["min"],
        data["GDP"].describe()["25%"],
        data["GDP"].describe()["75%"],
        data["GDP"].describe()["max"]]
    data["GDP Group"] = pd.cut(
        data["GDP"], bins, precision=0, labels=[
            "Low", "Mid", "High"])
    plt.figure(figsize=(15, 10))
    sns.barplot("avg_aqi", "Death_rate", hue="GDP Group", data=data)
    plt.xlabel("Air Quality Index (5: Very Poor, 1: Good)")
    plt.ylabel(
        "Ambient air pollution attributable death rate (per 100 000 population)")
    plt.title("Plot showing the relationship between Air Quality and Death rates due \
              to air pollution with respect to GDP category of the country")
    plt.show()
    # Plot
    plt.figure(figsize=(15, 10))
    sns.scatterplot('GDP',
                    'Death_rate',
                    size="Pop_Density",
                    hue="avg_aqi",
                    palette="viridis",
                    sizes=(50,
                           1000),
                    data=data.iloc[0:50])
    plt.xlabel("GDP (US$ million)")
    plt.ylabel(
        "Ambient air pollution attributable death rate (per 100 000 population)")
    plt.title("Plot showing the relationship between death rates due to air pollution and \
    			 country level characteristics: Air quality, GDP and Population Density")
    plt.show()

    return


if __name__ == '__main__':
    log.setLevel("ERROR")
    default_function()


