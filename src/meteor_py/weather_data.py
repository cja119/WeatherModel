"""
This is the WeatherData class, which is used to access and sample meteorological data from NASA's MERRA-2 dataset.
"""


from numpy import datetime64
from earthaccess import login, search_data, download 
from xarray import open_mfdataset, concat
from .errors import  WSDataFeedError
from .sampling import geospatial_sampling, time_sampling
from .plots import globalplot,boxplot,timeseriesplot
from os import getcwd, getenv
from typing import Optional
from pathlib import Path


class WeatherData:
        """""
        The meteorological class sets up the data and samples it in accordance with the hyperparameters as specified. 
        This includes allowing for a four vertex polygon. 
        
                date:                   tuple[datetime64,datetime64]    -> Start and end date of modelling.
                location:               string                          -> Name of place being modelled (for graphs)
                wind:                   boolean                         -> Is it a windfarm?
                solar:                  boolean                         -> Is it a solar farm?
                interval:               integer                         -> Sampling interval (seconds).
                storage_location:       string                          -> Storage location for merra2 files.
                n_samp:                 integer                         -> Number of samples to be taken (for random-time sampling).
                sample_type:            string                          -> "Structured" or "Random"
                latitudes:              tuple[float,float]              -> (Min,Max) Latitudes for the region of interest.
                longitudes              tuple[float,float]              -> (Min,Max) Longitudes for the region of interest. 
                
                
        """
        def __init__(
                      self,
                      date: tuple[datetime64,datetime64], 
                      location: str, 
                      wind: bool = False, 
                      solar: bool = False, 
                      interval: int = 3600,\
                      storage_location: Optional[str] = None,
                      n_samp: int = 100,
                      sample_type: str = "Structured",
                      latitudes: tuple[float,float] = (-90,90),
                      longitudes: tuple[float,float ] =(-180,180),
                      environment_login: bool = False
                      ):
                
                if storage_location is None:
                    storage_location = Path(__file__).resolve().parent.parent / "data/cache"
                    

                # Setting boolean hyperparameters and location descriptor
                self.wind = wind
                self.solar = solar
                self.location = location
                self.storage_location = storage_location
                        
                # Setting temporal and spatial parameters
                self.date_lower = date[0]
                self.date_upper = date[1]
                

                 # Ensuring the lattitudes and longitudes are in the correct order 
                if latitudes[0] > latitudes[1]:
                        self.latitudes = (latitudes[1],latitudes[0])
                        latitudes = self.latitudes
                else: 
                    self.latitudes  = latitudes
                if longitudes[0] > longitudes[1]:
                        self.longitudes = (longitudes[1],longitudes[0])
                        longitudes = self.longitudes
                else:
                    self.longitudes = longitudes
                        
                # Trying to load data from an existing model, saved as a .pickel file in the 'MetData' folder

                # Setting the time interval (in seconds) and accessing data from NASA's merra2 library. 
                self.interval   = interval               
                self.get_data(
                       interval,
                       storage_location=storage_location,
                       environment_login=environment_login
                       )

                # Sampling the datasets to generate the requisite dataframes
                if self.solar:
                        self.solar_data_spatial = geospatial_sampling(
                               self.solar_data,
                               latitudes,
                               longitudes
                               )
                        self.solar_data_spatial_temporal  = time_sampling(
                                self.solar_data_spatial,
                                sample_type,
                                interval,
                                n_samp
                                )
                self.wind_data_spatial = geospatial_sampling(
                       self.wind_data,
                       latitudes,
                       longitudes
                       )
                self.wind_data_spatial_temporal = time_sampling(
                        self.wind_data_spatial,
                        sample_type,
                        interval,
                        n_samp
                        )                
 

        def get_data(self, 
                     interval,
                     storage_location,
                     environment_login
                     ): 
                """
                This code will access data from the NASA Merra2 dataset, and return that in the form of an xarray dataset.
                Currently this only works for wind and solar data, but may be expanded in the futur
                """
                
                if environment_login:
                    _ = login(strategy="environment",persist=True)
                else:  
                    _ = login()
                        

                if self.solar:
                        solar_online = search_data(short_name="M2T1NXRAD",
                                            cloud_hosted=False,
                                            temporal = (f"{(self.date_lower)}"[0:10],f"{(self.date_upper)}"[0:10]))
                        solar_files  = download(solar_online,storage_location)
                        
                        self.solar_data =  open_mfdataset(solar_files,engine='netcdf4')
                
                # This grabs the wind speed data to use in the model. 
                wind_online = search_data(short_name="M2T1NXSLV",
                                cloud_hosted=False,
                                temporal = (f"{(self.date_lower)}"[0:10],f"{(self.date_upper)}"[0:10]))

                # This will download the datasets.                         
                wind_files  = download(wind_online,storage_location)
                self.wind_data =  open_mfdataset(wind_files,engine='netcdf4')

                            
                
 
                if not self.wind and not self.solar:
                        raise(WSDataFeedError)
                else: 
                        pass
        
        def global_plot(self):
                globalplot(self)
                pass
        
        def box_plot(self):
                boxplot(self)
                pass

        def time_series_plot(self):
                timeseriesplot(self)
                pass
