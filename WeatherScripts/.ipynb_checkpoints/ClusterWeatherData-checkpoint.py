import sys
import os


# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../')
sys.path.append(module_folder_path)



from os import getcwd, chdir
from pickle import load
import numpy as np
from ClusteringScripts.Wards_Method import *
from sklearn import tree
from ClusteringScripts.Kmeans import *
from ClusteringScripts.Wards_Method import *
from MeteorologicalScripts.DemandProfile import *

dir = getcwd()
chdir(dir+'/PreOptimisationDataStore')
with open('WeatherData.pickle', 'rb') as f:
    df = load(f)
chdir(dir)
start_date   =  np.datetime64('2022-01-01', 'ns') 
end_date     = np.datetime64('2023-01-01', 'ns') 

clustered_array = consecutive_clustering(df,1000,'medoid')
predictions = [item for i in clustered_array for item in [i[0]] * int(i[1])]

clustered_times = [[0,0]]
for i in range(1,len(clustered_array)+1):
    clustered_times.append([int(clustered_times[i-1][1]+clustered_times[i-1][0]),int(clustered_array[i-1][1])])

stacked_array = generate_stacked_array(start_date,end_date,200,8,360)
time_array = insert_array(stacked_array,np.array(clustered_times[1:]))
wind_speed = []
for t in time_array:
    wind_speed.append(predictions[t[0]])


demand_signal = Demand_profle(number_points = time_array[-1,0]+1 ,
                              number_time_steps = 50,
                              peak_seasonal_demand =0.25,
                              net_frequency = 1,
                              net_ramp = 0.2,
                              baseline = 1,
                              net_demand = 8.16*10**(8)/425.445/7,
                              stochasticity = 0.2,
                              amplitude = 0.2
                              )

save_csv(time_array[:,0],'time_data.csv')
save_csv(time_array[:,1],'time_duration.csv')
save_csv(wind_speed,'wind_speed.csv')
sampled_signal = [demand_signal.interpolate[i] for i in time_array[:,0]]
save_csv(sampled_signal, 'demand_signal.csv')
