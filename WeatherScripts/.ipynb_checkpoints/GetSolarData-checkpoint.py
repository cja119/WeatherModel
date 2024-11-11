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
from MeteorologicalScripts.RenwableEnergyModelling import RenewableEnergy
from MeteorologicalScripts.DemandProfile import *
from ClusteringScripts.Kmeans import *
from PreOptimisationDataStore.DefaultParameters import Default_Params
from os import getcwd,chdir
from pickle import dump,load

points = [(sys.argv[0],sys.argv[3]),(sys.argv[0],sys.argv[3]),(sys.argv[1],sys.argv[2]),(sys.argv[1],sys.argv[2])]
start_date   =  np.datetime64('2022-01-01', 'ns') 
end_date     = np.datetime64('2023-01-01', 'ns') 
location = 'Coastal Chile'
solar = True
#latitudes = (-24,-23)
#longitudes = (-68,-67)

weatherdata = Meteorological(date = (start_date,end_date),
                                location= 'Chile', 
                                wind = False,
                                solar = solar, 
                                latitudes =(sys.argv[0], sys.argv[1]), 
                                longitudes =(sys.argv[2],sys.argv[3])
                                )


RenewableEnergy(weatherdata, points).export_power(weatherdata,name='SolarData', dates=True)