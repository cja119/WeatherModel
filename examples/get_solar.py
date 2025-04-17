"""
This script is used to generate solar data for a given location and time period using the WeatherData 
    class from the weathermodel module.
It takes the following command line arguments:
    1. Latitude of the first location
    2. Longitude of the first location
    3. Latitude of the second location
    4. Longitude of the second location
"""

from scipy.spatial.distance import cdist
import numpy as np
import pandas as pd
from weathermodel import *
import sys
from os import getcwd,chdir
from pickle import dump,load

start_date =  np.datetime64('2022-01-01', 'ns') 
end_date    = np.datetime64('2023-01-01', 'ns') 
location = 'Coastal Chile'
solar = True
#latitudes = (-24,-23) -24, -23, -68, -67
#longitudes = (-68,-67)

weatherdata = WeatherData(
    date = (start_date,end_date),
    location= 'Chile', 
    wind = False,
    solar = solar, 
    latitudes =(sys.argv[0], sys.argv[1]), 
    longitudes =(sys.argv[2],sys.argv[3])
    )


RenewableEnergy(weatherdata).export_power(
    weatherdata,
    name='SolarData',
    dates=True
    )