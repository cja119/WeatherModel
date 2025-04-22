"""
This script is used to generate wind data for a given location and time period using the WeatherData 
    class from the weathermodel module.
It takes the following command line arguments:
    1. Latitude of the first location
    2. Longitude of the first location
    3. Latitude of the second location
    4. Longitude of the second location
"""

import sys
from numpy import datetime64
from meteor_py import *

start_date   =  datetime64('2022-01-01', 'ns') 
end_date     = datetime64('2023-01-01', 'ns') 

weatherdata = WeatherData(
    date=(start_date, end_date),
    location='Coastal Chile',
    wind=True,
    solar=False,
    interval=3600,
    n_samp=100,
    sample_type="Structured",
    latitudes=(sys.argv[0], sys.argv[1]),
    longitudes=(sys.argv[2], sys.argv[3])
)

renewableenergy = RenewableEnergy(
    weatherdata,
    [
        (0, 0.0),       # These are points along the power curve.
        (3, 0.0),       # are used in the output curve.
        (4, 0.648),     # Wind speeds are in [m/s].
        (5, 1.4832),
        (6, 2.736),
        (7, 4.4676),
        (8, 6.7104),
        (9, 9.3168),
        (10, 11.2392),
        (11, 11.8008),
        (12, 11.8728),
        (13, 11.88),
        (30, 11.88),
    ]
)

RenewableEnergy(weatherdata).export_power(weatherdata,name='WindData', dates=True)