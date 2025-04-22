"""
This code implements the renewable energy class which calculates the power output of a wind and solar farm
based on the weather data provided. 
"""

from .sampling import geospatial_sampling
from .plots import boxplot
from .wards_method import consecutive_clustering
from shapely.geometry import Polygon, Point, shape
from numpy import array, meshgrid, zeros, trapz, mean, exp, log, pi, nan
import numpy as np
from pandas import DataFrame
from pysolar.solar import get_altitude
from xarray import Dataset
from pyproj import Proj
from datetime import datetime, timezone
from .weather_data import WeatherData
from pathlib import Path

class RenewableEnergy:
    def __init__(
            self,
            weather_data: WeatherData, 
            power_curve: None, 
            min_radius: float = 100, 
            cluster = False, 
            num_clusters = 1000
            ):
        
        """
        This class implements the renewable energy model, which calculates the power output of a wind and solar farm
        based on the weather data provided.
        weather_data:    WeatherData         -> The weather data to be used.
        power_curve:     list(tuple[float,float]) -> A list of tuples of (wind speed [m/s], power output).
        min_radius:      float               -> The minimum radius of the windfarm [m].
        cluster:         Boolean             -> Whether or not the windfarm is clustered.
        num_clusters:    int                 -> The number of clusters to be used.
        """
        
        self.min_radius     = min_radius  
        self.cluster        = cluster
        lons = weather_data.longitudes
        lats = weather_data.latitudes
        self.vertices = [
            (lats[0],lons[1]),
            (lats[1],lons[1]),
            (lats[1],lons[0]),
            (lats[0],lons[0])
            ]
        
        if weather_data.wind:
            self.allocate_windfarm(weather_data)
            self.wind_power_output(
                weather_data,
                power_curve,
                cluster=cluster,
                num_clusters=num_clusters
                )
        if weather_data.solar:
            self.allocate_solarfarm(weather_data)

    def allocate_windfarm(self,weather_data, plot: bool = False):
        ''' NB, this sampling only works on convex domains
        
        plot:       Boolean -> Whether a plot of the windfarm is desired. 
        '''

        # Generating ordered lists of vertex coordinates.
        longitudes = weather_data.longitudes
        latitudes  = weather_data.latitudes

        # Sampling the data within these coordinates. 
        square_datset = geospatial_sampling(
            weather_data.wind_data_spatial_temporal,
            latitudes,
            longitudes
        )

        # Filtering these points to turn the square dataset into only points enclosed within the polygon. 
        filtered, lats, lons = self.filter_points(self.vertices,square_datset)
        
        # Generating a geographic projection of the polygon.
        pa = Proj("+proj=aea +lat_1=37.0 +lat_2=41.0 +lat_0=39.0 +lon_0=-106.55")
        x, y = pa(list(zip(*self.vertices))[1], list(zip(*self.vertices))[0])
        cop = {"type": "Polygon", "coordinates": [zip(x, y)]}

        # Plotting, if the boolean plot is set to true.
        if plot:
            boxplot(weather_data, points=list(zip(lats,lons)), just_wind=True,vertices = self.vertices)
        
        # Setting these values as attributes as they can be useful to access later on. 
        self.fitered        = filtered
        self.latitudes      = lats
        self.longitudes     = lons
        self.meanU          = filtered.variables['U10M'].mean(dim=['lat', 'lon'],keep_attrs=True)
        self.meanV          = filtered.variables['V10M'].mean(dim=['lat', 'lon'],keep_attrs=True)
        self.meanspeed      = (filtered.variables['U10M'].mean(dim=['lat', 'lon'],keep_attrs=True)**2 \
                               + filtered.variables['U10M'].mean(dim=['lat', 'lon'],keep_attrs=True)**2)**0.5
        self.time           = filtered.variables['time']
        area                = shape(cop).area
        area_km             = area/ 1000000
        self.area           = {'m2': area, 'km2': area_km}
        self.num_turbines   = int((self.area['m2'] * (pi / (2*(3**0.5)))) / (pi*self.min_radius**2))
        pass
    
    def allocate_solarfarm(self,weather_data, plot: bool = False):
        """
        NB, this sampling only works on convex domains
        weather_data:    WeatherData         -> The weather data to be used.
        plot:       Boolean -> Whether a plot of the windfarm is desired.
        """
        
        # Generating ordered lists of vertex coordinates.
        longitudes = weather_data.longitudes
        latitudes  = weather_data.latitudes

        # Sampling the data within these coordinates.   
        square_datset = geospatial_sampling(
            weather_data.solar_data_spatial_temporal,
            latitudes,
            longitudes
            )

        # Filtering these points to turn the square dataset into only points enclosed within the polygon. 
        filtered, lats, lons = self.filter_points(self.vertices,square_datset)

        square_datset_wind = geospatial_sampling(
            weather_data.wind_data_spatial_temporal,
            latitudes,
            longitudes
            )

        # Filtering these points to turn the square dataset into only points enclosed within the polygon. 
        filtered_wind, _, _ = self.filter_points(self.vertices,square_datset_wind)

        # Generating a geographic projection of the polygon.
        pa = Proj("+proj=aea +lat_1=37.0 +lat_2=41.0 +lat_0=39.0 +lon_0=-106.55")
        x, y = pa(list(zip(*self.vertices))[1], list(zip(*self.vertices))[0])
        cop = {"type": "Polygon", "coordinates": [zip(x, y)]}

        # Plotting, if the boolean plot is set to true.
        if plot:
            boxplot(weather_data,
                    points = list(zip(lats,lons)),
                    just_solar = True,
                    vertices = self.vertices
                    )
        
        # Getting the necessary solar panel performance parameters      
        self.filtered         = filtered
        self.latitudes        = lats
        self.longitudes       = lons
        
        # Inside allocate_solarfarm or wherever solar calculations are done
        swgdn_mean = self.filtered['SWGDN'].mean(dim=['lat', 'lon'], keep_attrs=True)
        swtdn_mean = self.filtered['SWTDN'].mean(dim=['lat', 'lon'], keep_attrs=True)
        albedo = self.filtered['ALBEDO'].mean(dim=['lat', 'lon'], keep_attrs=True).fillna(0)
        
        self.clearness_index = swgdn_mean / swtdn_mean.where(swtdn_mean != 0, other=1)
        self.clearness_index = self.clearness_index.where(swtdn_mean != 0, other=0)
        self.diffuse_fraction = np.clip(1 / (1 + np.exp(-5.0033 + 8.6025 * self.clearness_index)), 0, 1)
        
        self.time             = filtered.variables['time']
        self.solar_zenith     = self.solar_zenith_angle(mean(lats), mean(lons), filtered.variables['time'])
        self.temperature      = filtered_wind.variables['T10M'].mean(dim=['lat', 'lon'],keep_attrs=True)
        
        # Calculating irradiance
        self.Global_Irr = swgdn_mean
        self.Diff_Irr = swgdn_mean * self.diffuse_fraction
        self.IDir_H = self.Global_Irr - self.Diff_Irr
        self.IDir_H = np.where(self.IDir_H < 0, 0, self.IDir_H)

        epsilon = 0.23 # Corresponds to a 85% tracking aperture
        cos_zenith = np.cos(self.solar_zenith)
        cos_zenith_safe = np.where(cos_zenith > epsilon, cos_zenith, np.nan)

        self.IDir_P = self.IDir_H / cos_zenith_safe
        self.IDir_P = np.where(cos_zenith > epsilon, self.IDir_P, 0)

        self.IDif_P = (self.Diff_Irr * (1 + cos_zenith) / 2 +
                        albedo * (self.Global_Irr) * (1 - cos_zenith) / 2)

        self.IDir_P = np.nan_to_num(self.IDir_P, nan=0)
        self.IDif_P = np.nan_to_num(self.IDif_P, nan=0)

        # Performance calculation with safeguard
        G_stand = 1000
        self.G_prime = (self.IDir_P + self.IDif_P) / G_stand
        g_prime_safe = np.where(self.G_prime <= 0, 1,self.G_prime)
        self.T_prime = (self.temperature - 298.15) + (self.IDir_P + self.IDif_P) * 0.015 # Windy Conditions
        self.K = [0.017162, 0.040289, 0.004681, 0.000148, 0.000169, 0.000005]
        self.eta_rel = (1\
            + self.K[0] * log(g_prime_safe) \
            + self.K[1] * (log(g_prime_safe))**2 \
            + self.T_prime * (self.K[2] + self.K[3] * log(g_prime_safe) \
            + self.K[4] * (log(g_prime_safe))**2) \
            + self.K[5] * self.T_prime**2
        )
        self.eta_rel = np.minimum(self.eta_rel,1)
        

        # Define a realistic maximum power output
        max_power_output = 1000  # Normal testing power ouput

        self.solar_power = np.maximum(0, self.eta_rel * self.G_prime)  # Ensure no negative values
        self.solar_power_output = np.minimum(
            self.solar_power * max_power_output,
            max_power_output
            )  # Apply saturation
        self.solar_capacity_factor = (np.mean(self.solar_power)).values
        pass

    def wind_power_output(
            self,
            weather_data:WeatherData,
            power_curve_points,
            temperature_range_k: tuple[float,float] = (248,323), 
            hub_height: float = 100,
            hellman_exponent = 0.15,
            cluster=False,
            num_clusters=1000
            ):
        '''
        This function generates a temporally indexed wind turbine power output, 
                based on the power curve of a turbine and the temporally indexed wind speed data.

        power_curve_points:     list(tuple[float,float])    -> A list of tuples of (wind speed [m/s], power output). 
                                                                    The same power units are output as those input.
        temperature_range_k:    tuple(float,float)          -> The operating temperatuer range of the turbine,
                                                                    in kelvin, lower temperature first.
        hub_height:             float                       -> Height of the turbine's hub [m].
        hellman_exponent        float                       -> Exponent for the wind-speed against height function. 
        '''
        # The below function allows for an interpolation of a wind turbines power curve.

        def power_curve(wind_speed,points):
                
            # Generating an empty array of windspeeds 
            wind_speed  = wind_speed.values
            power       = zeros(len(wind_speed))

            # Iterating over the list of windspeeds in order to generate a list of power outputs. 
            for j in range(len(wind_speed)):
                if wind_speed[j] >= points[-1][0]:
                    power[j] = 0
                else:
                    for i in range(len(points)-1):
                        if wind_speed[j] >= points[i][0] and wind_speed[j] <= points[i+1][0]:
                            power[j] = ((wind_speed[j] - points[i][0])\
                                        / (points[i+1][0] - points[i][0])) * \
                                            (points[i+1][1] - points[i][1]) \
                                                + points[i][1]
                            break 
            return power

        # Calculating the wind speed at the height of the hub (default MERRA-2 is at 10m). 
        self.wind_speed_hub_height = self.meanspeed * (hub_height / 10)**hellman_exponent

        # Calculating the turbine power output
        power_output = power_curve(self.wind_speed_hub_height,power_curve_points)

        # Dropping all values of power output that occur when the ambient temperature is out of the operating range of the turbine.  
        temperature_data  = weather_data.wind_data_spatial_temporal.variables['T10M'].mean(dim=['lat','lon']).values
        conditions = [
            all(
                [temperature_data[i] >= temperature_range_k[0], temperature_data[i] <= temperature_range_k[1]]
                ) for i in range(len(temperature_data))
            ]
        self.wind_power = power_output[conditions]

        if cluster:
            self.wind_power = consecutive_clustering(
                DataFrame(
                    {
                        "Wind Data": self.wind_power,
                        "Start Date": weather_data.date_lower,
                        "End Date": weather_data.date_upper
                        }
                        ),
                        num_clusters,
                        update_strategy='medoid'
                        )
            
        # Calculating a capacity factor for the wind farm. 
        self.wind_capacity_factor = trapz(self.wind_power, dx = weather_data.interval) \
            / (power_curve_points[-1][1] * weather_data.interval * len(self.wind_power))
        pass

    def export_power(
            self,
            weather_data: WeatherData,
            name: str,
            location=None,
            dates=True
            ):
        '''
        This function saves the wind speed data in a csv, if required.

        name:   string      -> Name of the CSV file
        dates:  booolean    -> Choice whether or not the time indices are to be stored in a column,
                                    to the left of the wind speed data.
        '''
        if location is None:
            location = Path(__file__).resolve().parent.parent / "data"
        
        if weather_data.wind:
            if dates:
                data = DataFrame(
                    {
                        "Wind Power [GJ/h]": self.wind_power,
                        "Start Date": weather_data.date_lower,
                        "End Date": weather_data.date_upper
                    }
                )
            else:
                data = DataFrame({"Wind Power [GJ/h]": self.wind_power})
            if self.cluster:
                data.to_csv('./'+location+'/'+name+'_Clustered_Wind.csv',sep=' ')
            else:
                data.to_csv('./'+location+'/'+name+'_Wind.csv',sep=' ')
        
        if weather_data.solar:
            if dates:
                data = DataFrame(
                    {
                        "Solar Power [kW]": self.solar_power_output,
                        "Start Date": weather_data.date_lower,
                        "End Date": weather_data.date_upper
                    }
                )
            else:
                data = DataFrame({"Solar Power [kW]": self.solar_power_output})
            data.to_csv('./'+location+'/'+name+'_Solar.csv',sep=' ')
        pass

    def solar_zenith_angle(self,lat, lon, time_utc_array):
        """
        This function calculates the solar zenith angle for a given latitude, longitude, and time.
        lat:            float   -> Latitude in degrees.
        lon:            float   -> Longitude in degrees.
        time_utc_array: array   -> Array of time values in UTC.
        Returns a xarray dataset with the solar zenith angle.
        """
        
        deg_to_rad = np.pi / 180.0
        
        def calculate_solar_altitude(time_utc):
            utc_time_str = str(time_utc.values)[:-10]  
            utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S")
            utc_time = utc_time.replace(tzinfo=timezone.utc)
            
            return get_altitude(lat, lon, utc_time) * deg_to_rad
        
        zenith_angles = np.array(
            [pi/2 - calculate_solar_altitude(time_utc) for time_utc in time_utc_array]
            )
        zenith_angle_dataset = Dataset(
            {'solar_zenith_angle': (time_utc_array.dims, zenith_angles)},
            coords={'time': time_utc_array}
            )
        return zenith_angle_dataset['solar_zenith_angle']
    
    def filter_points(self,coordinates, world_test):
        """
        This function filters the points within the polygon defined by the coordinates.
        coordinates:    list(tuple[float,float])    -> A list of tuples of (latitude, longitude) coordinates.
        world_test:     xarray.Dataset              -> The dataset to be filtered."""
        # Generating a polygon from the coordinates. 
        polygon = Polygon(coordinates)

        # Generating latitude and longitude values.
        latitudes = world_test['lat'].values
        longitudes = world_test['lon'].values

        # Building a meshgrid of these values and flattening it.
        lon_grid, lat_grid = meshgrid(longitudes, latitudes)
        lon_flat = lon_grid.flatten()
        lat_flat = lat_grid.flatten()
        
        # Assembling the points into coordinates
        points = [Point(lat, lon) for lat, lon in zip(lat_flat, lon_flat)]

        # Generating an array boolean based onwhether the coordinates are within the polygon. 
        mask = array([polygon.contains(point) for point in points])
        mask_2d = mask.reshape(lon_grid.shape)

        # Producing filtered points and xarray dataset and returning these as the function output. 
        filtered_latitudes  = lat_grid[mask_2d]
        filtered_longitudes = lon_grid[mask_2d]
        filtered_world_test = world_test.where(mask_2d)

        return filtered_world_test, filtered_latitudes, filtered_longitudes
