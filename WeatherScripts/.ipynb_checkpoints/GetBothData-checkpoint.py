import sys
import os

# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../')
sys.path.append(module_folder_path)


from scipy.spatial.distance import cdist
import numpy as np
import pandas as pd
from MeteorologicalScripts.GetWeatherData import Meteorological
from MeteorologicalScripts.RenewableEnergyModelling import RenewableEnergy
from MeteorologicalScripts.DemandProfile import *
from MeteorologicalScripts.Wards_Method import *
from os import getcwd,chdir
from pickle import dump,load


start_date   =  np.datetime64('2023-01-01', 'ns') 
end_date     = np.datetime64('2024-01-01', 'ns') 

print(f'Lats: {(float(sys.argv[1]), float(sys.argv[2]))}')
print(f'Lons: {(float(sys.argv[3]),float(sys.argv[4]))}')

weatherdata = Meteorological(date = (start_date,end_date),
                                location= 'Coastal Chile', 
                                wind = True,
                                solar = True, 
                                interval = 3600,
                                storage_location =module_folder_path+"/WeatherData", 
                                n_samp = 100, 
                                sample_type = "Structured", 
                                latitudes =(float(sys.argv[1]), float(sys.argv[2])), 
                                longitudes =(float(sys.argv[3]),float(sys.argv[4])),
                                environment_login=True
                                )


renewableenergy =    RenewableEnergy(weatherdata,
                                        [(0,0.0),       # These are points along the power curve. 
                                            (3,0.0),       # are used in the ouput curve.
                                            (4,0.648),     # Wind speeds are in [m/s].
                                            (5,1.4832),
                                            (6,2.736),
                                            (7,4.4676),  
                                            (8,6.7104),
                                            (9,9.3168),
                                            (10,11.2392),
                                            (11,11.8008),
                                            (12,11.8728),
                                            (13,11.88),
                                            (30,11.88),
                                            ]
                                            )



renewableenergy.export_power(weatherdata,name='CoastalChile', dates=False)
