from matplotlib.pyplot import figure, axes, contourf, title, colorbar, cm, subplots, xticks, show, scatter, fill
from cartopy.crs import Robinson, PlateCarree, AlbersEqualArea, Mercator, Stereographic
from cartopy.feature import NaturalEarthFeature, BORDERS, OCEAN, LAND, LAKES
from numpy import datetime64
from MeteorologicalScripts.SampleWeatherData import time_sampling
from numpy import arange, meshgrid, mean

def globalplot(self):
    '''This generates a 'global' plot of the given dataset.
    If two different dates are given, the code will calculate the average value of the parameter at that location.
    '''
    if self.wind:
        wind_samples = time_sampling(self.wind_data, graph = True, time_data = (self.date_lower, self.date_upper))
    if self.solar:
        solar_samples = time_sampling(self.solar_data, graph = True, time_data = (self.date_lower, self.date_upper))

    if self.wind:
        # Averaging the wind speed temporally. 
        wind_mean   = wind_samples.mean(dim = 'time')

        # Calculating the l^2 norm of the wind velocity. 
        wind_mag    = (wind_mean.variables['U10M'][:,:]**2 + wind_mean.variables['V10M'][:,:]**2)**0.5

        # Extracting the longitude and latitude values, and taking the values at initial and terminal time. 
        wind_lons   = wind_mean.variables['lon'][:]
        wind_lats   = wind_mean.variables['lat'][:]
        wind_date_l = wind_samples.variables['time'][0]
        wind_date_u = wind_samples.variables['time'][-1]

        # Generating a mesgrid of the latitudes and longitude values. 
        wind_lon, wind_lat = meshgrid(wind_lons, wind_lats)

        # These plots can take a while to generate...
        print(f"Plotting average wind speed data at 10m on time span: {str(wind_date_l.values)[0:10]} at {str(wind_date_l.values)[11:16]} to {str(wind_date_u.values)[0:10]} at {str(wind_date_u.values)[11:16]}")
        print("This may take up to 5 minutes...")
            
        # Generating the plots
        fig = figure(figsize=(8,4)); 
        ax  = axes(projection=Robinson()); 
            
         # Clevs sets the range that is plotted on the colourmap
        ax.set_global()
        ax.coastlines(resolution="110m",linewidth=1); 
        ax.gridlines(linestyle='--',color='black')
        clevs = arange(0.99*wind_mag[:,:].min(),1.01*wind_mag[:,:].max(),(wind_mag[:,:].max()-wind_mag[:,:].min())/100)
        contourf(wind_lon, wind_lat, wind_mag[:,:], clevs, transform=PlateCarree(),cmap=cm.jet)
        title(f'Average MERRA-2 Wind Speed at 10m \n On time span: {str(wind_date_l.values)[0:10]} at {str(wind_date_l.values)[11:16]} to {str(wind_date_u.values)[0:10]} at {str(wind_date_u.values)[11:16]} ', size=14)
            
        # Generating a colorbar, giving a scale. 
        cb = colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16, shrink=0.8)
        cb.set_label('m/s',size=12,rotation=0,labelpad=15); cb.ax.tick_params(labelsize=10)
        
    if self.solar:
        # Averaging the solar irradiation, temporally. 
        solar_mean = solar_samples.mean(dim = 'time')

        # Finding the madnitude of solar radiation 
        solar_mag  = solar_mean.variables['SWTDN']

        # Extracting the longitude and latitude values, and taking the values at initial and terminal time. 
        solar_lons = solar_mean.variables['lon'][:]
        solar_lats = solar_mean.variables['lat'][:]
        solar_date_l = solar_samples.variables['time'][0]
        solar_date_u = solar_samples.variables['time'][-1]

        # Generating a mesgrid of the latitudes and longitude values. 
        solar_lon, solar_lat = meshgrid(solar_lons, solar_lats)


        # These plots can take a while to generate...   
        print(f"Plotting average surface solar radiation data on time span: {str(solar_date_l.values)[0:10]} at {str(solar_date_l.values)[11:16]} to {str(solar_date_u.values)[0:10]} at {str(solar_date_u.values)[11:16]}")
        print("This may take up to 5 minutes...")
            
        # Generating the plots
        fig = figure(figsize=(8,4))
        ax  = axes(projection=Robinson()) 

        # Clevs sets the range that is plotted on the colourmap
        ax.set_global()
        ax.coastlines(resolution="110m",linewidth=1); ax.gridlines(linestyle='--',color='black')            
        clevs = arange(0.99*solar_mag[:,:].min(),1.01*solar_mag[:,:].max(),(solar_mag[:,:].max()-solar_mag[:,:].min())/100)
        contourf(solar_lon, solar_lat, solar_mag[:,:], clevs, transform=PlateCarree(),cmap=cm.jet)
        title(f'Average MERRA-2 Surface Solar Radiation \n On time span: {str(solar_date_l.values)[0:10]} at {str(solar_date_l.values)[11:16]} to {str(solar_date_u.values)[0:10]} at {str(solar_date_u.values)[11:16]} ', size=14)
        cb = colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16, shrink=0.8)
        cb.set_label('W/m2',size=12,rotation=0,labelpad=15); cb.ax.tick_params(labelsize=10)
    pass

def boxplot(self, points = [(1,1)], just_wind = False, just_solar = False, vertices = [(0,0)]):
    '''This generates a 'box' plot of the given dataset.
    If two different dates are given, the code will calculate the average value of the parameter at that location.
    
    points:     list(tuple(float,float))    -> list of lon/lat coordinates of solar panels / wind turbines.
    just_wind:  boolean                     -> if only 1 plot is required for the wind farm.
    just_solar: boolean                     -> if only 1 plot is required for the solar farm.
    vertices:   list(tuple(float,float))    -> these are the corners of the polygon that describes the wind or solar farm. 
    
    '''

    # Generating sample datasets - as this is a box plot, the data can be reduced in size. 
    if self.wind and not just_solar:
        wind_samples = time_sampling(self.wind_data, graph = True, time_data = (self.date_lower, self.date_upper))
        small_wind_samples = time_sampling(self.wind_data_spatial, graph = True, time_data = (self.date_lower, self.date_upper))
    if self.solar and not just_wind:
        solar_samples = time_sampling(self.solar_data, graph = True, time_data = (self.date_lower, self.date_upper))
        small_solar_samples = time_sampling(self.solar_data_spatial, graph = True, time_data = (self.date_lower, self.date_upper))

    # Finding the bounds of the vertices and the central points to align the map
    extent = [*self.longitudes, *self.latitudes]
    central_lon = mean(extent[:2])
    central_lat = mean(extent[2:])
        
    if self.wind and not just_solar:

         # Averaging the wind speed temporally
        wind_mean = wind_samples.mean(dim = 'time')
        small_wind_mean = small_wind_samples.mean(dim = 'time')

        # Calculating the l^2 norm of the wind velocity. 
        wind_mag = (wind_mean.variables['U10M'][:,:]**2 + wind_mean.variables['V10M'][:,:]**2)**0.5
        small_wind_mag = (small_wind_mean.variables['U10M'][:,:]**2 + small_wind_mean.variables['V10M'][:,:]**2)**0.5
        
        # Extracting the longitude and latitude values, and taking the values at initial and terminal time. 
        wind_lons = wind_mean.variables['lon'][:]
        wind_lats = wind_mean.variables['lat'][:]
        wind_date_l = wind_samples.variables['time'][0]
        wind_date_u = wind_samples.variables['time'][-1]

        # Generating a mesgrid of the latitudes and longitude values. 
        wind_lon, wind_lat = meshgrid(wind_lons, wind_lats)

        # These plots can take a while to generate... 
        print(f"Plotting average wind speed data at 10m on time span: {str(wind_date_l.values)[0:10]} at {str(wind_date_l.values)[11:16]} to {str(wind_date_u.values)[0:10]} at {str(wind_date_u.values)[11:16]}")
        print("This may take up to 5 minutes...")

        # Generating the plots
        fig = figure(figsize=(8,8)); ax  = axes(projection=Stereographic(central_lon, central_lat)); ax.set_extent(extent); ax.gridlines()
        rivers_50m = NaturalEarthFeature('physical', 'rivers_lake_centerlines', '50m')
        
        # Clevs sets the range that is plotted on the colourmap.
        ax.add_feature(BORDERS, linestyle='-', alpha=1)
        ax.add_feature(OCEAN,facecolor=("lightblue"))
        ax.add_feature(LAND, edgecolor='black')
        ax.add_feature(LAKES, edgecolor='black')
        ax.add_feature(rivers_50m, facecolor='None', edgecolor='blue', linestyle=':')
        ax.coastlines(resolution='10m', color='black', linestyle='-', alpha=1,linewidth=2)
        clevs = arange(0.95*small_wind_mag[:,:].min(),1.05*small_wind_mag[:,:].max(),(small_wind_mag[:,:].max()-small_wind_mag[:,:].min())/100)
        contourf(wind_lon, wind_lat, wind_mag[:,:], clevs, transform=PlateCarree(),cmap=cm.jet,zorder = 1)
        title(f'Average MERRA-2 Wind Speed at 10m \n On time span: {str(wind_date_l.values)[0:10]} at {str(wind_date_l.values)[11:16]} to {str(wind_date_u.values)[0:10]} at {str(wind_date_u.values)[11:16]} ', size=14)
        cb = colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16, shrink=0.8)
        cb.set_label('m/s',size=12,rotation=0,labelpad=15); cb.ax.tick_params(labelsize=10)
        
        # Points refers to lon/lat coordinates of wind turbines. This allows for the windfarm to be overlayed on the contour plot
        if points != [(1,1)]:
           scatter([*list(zip(*points))[1]],[*list(zip(*points))[0]], zorder=2,transform=PlateCarree(), marker='o',s=10, facecolors='black',edgecolors='black')
           for lat, lon in vertices:
                scatter(lon, lat, marker='o', color='red', edgecolors='black', s=10,transform=PlateCarree(), zorder=3)
                ax.text(lon, lat, f'({lon},{lat})', transform=PlateCarree(),color='red',ha='right', va='bottom', fontsize=8, zorder = 4)
               
    if self.solar and not just_wind:

        # Averaging the solar irradiation, temporally. 
        solar_mean = solar_samples.mean(dim = 'time')
        small_solar_mean = small_solar_samples.mean(dim = 'time')

        # Finding the madnitude of solar radiation 
        solar_mag  = solar_mean.variables['SWTDN']
        small_solar_mag = small_solar_mean.variables['SWTDN']


        # Extracting the longitude and latitude values, and taking the values at initial and terminal time. 
        solar_lons = solar_mean.variables['lon'][:]
        solar_lats = solar_mean.variables['lat'][:]
        solar_date_l = solar_samples.variables['time'][0]
        solar_date_u = solar_samples.variables['time'][-1]

        # Generating a mesgrid of the latitudes and longitude values. 
        solar_lon, solar_lat = meshgrid(solar_lons, solar_lats)

        # These plots can take a while to generate... 
        print(f"Plotting average surface solar radiation data on time span: {str(solar_date_l.values)[0:10]} at {str(solar_date_l.values)[11:16]} to {str(solar_date_u.values)[0:10]} at {str(solar_date_u.values)[11:16]}")
        print("This may take up to 5 minutes...")

        # Generating the plots
        fig = figure(figsize=(8,8)); ax  = axes(projection=Stereographic(central_lon, central_lat)); ax.set_extent(extent); ax.gridlines()
        rivers_50m = NaturalEarthFeature('physical', 'rivers_lake_centerlines', '50m')
        
        # Clevs sets the range that is plotted on the colourmap.
        ax.add_feature(BORDERS, linestyle='-', alpha=1)
        ax.add_feature(OCEAN,facecolor=("lightblue"))
        ax.add_feature(LAND, edgecolor='black')
        ax.add_feature(LAKES, edgecolor='black')
        ax.add_feature(rivers_50m, facecolor='None', edgecolor='blue', linestyle=':')
        ax.coastlines(resolution='10m', color='black', linestyle='-', alpha=1,linewidth=2)
        clevs = arange(0.95*small_solar_mag[:,:].min(),1.05*small_solar_mag[:,:].max(),(small_solar_mag[:,:].max()-small_solar_mag[:,:].min())/100)
        contourf(solar_lon, solar_lat, solar_mag[:,:], clevs, transform=PlateCarree(),cmap=cm.jet,zorder = 1)
        title(f'Average MERRA-2 Surface Solar Radiation \n On time span: {str(solar_date_l.values)[0:10]} at {str(solar_date_l.values)[11:16]} to {str(solar_date_u.values)[0:10]} at {str(solar_date_u.values)[11:16]} ', size=14)
        cb = colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16, shrink=0.8)
        cb.set_label('W/m2',size=12,rotation=0,labelpad=15); cb.ax.tick_params(labelsize=10)
        
        # Points refers to lon/lat coordinates of solar panels. This allows for the solarfarm to be overlayed on the contour plot
        if points != [(1,1)]:
            scatter([*list(zip(*points))[1]],[*list(zip(*points))[0]], zorder=3,transform=PlateCarree(), marker='o',s=10, facecolors='black' ,edgecolors='black')
            fill([*list(zip(vertices))[1]],[*list(zip(vertices))[0]],zorder = 2, color='grey', alpha = 0.5)
            for lat, lon in vertices:
                scatter(lon, lat, marker='o', s=10, color='red', edgecolors='black', transform=PlateCarree(), zorder=4)
                ax.text(lon, lat, f'({lon},{lat})', transform=PlateCarree(),color='red', ha='right', va='bottom', fontsize=8, zorder = 5)            
    pass

def timeseriesplot(self, position: tuple[float,float] = (1000,1000),xy=([0],[0]),title='.',xlabel='.',ylabel='.', zeroy: bool = False):
    ''' This script will generate a 2D timeseries plot of the meterological data for a single position.
    - If you don't specify a position, the default will take an average value accross all points within the square of meterological.longitudes x meterological.latitudes
    - surpess_wind and supress_solar, if set to 'False' will prevent the script from generating plots for wind and solar respectivly

    '''
    if position == (1000,1000) and all(xy[0][i] == 0 for i in range(len(xy[0]))) and all(xy[1][i] == 0 for i in range(len(xy[1]))):
        position = (mean(self.latitudes),mean(self.longitudes))
        

        
        if self.wind:
            magnitude = (self.wind_data_spatial_temporal.variables['U10M']**2 + self.wind_data_spatial_temporal.variables['V10M']**2)**0.5
            mean_wind = magnitude.mean(dim=('lat','lon'))

            fig, ax = subplots()
            ax.plot( self.wind_data_spatial_temporal.variables['time'],mean_wind,color = '#800020')
            ax.set(xlabel='time', ylabel='Wind Speed (m/s)',
                title=f'Temporal Variation in Wind Speed for {self.location}')
            xticks(rotation=90)
            ax.grid()
            show()

        
        if self.solar:
            magnitude = self.solar_data_spatial_temporal.variables['SWTDN']
            mean_solar      = magnitude.mean(dim=('lat','lon'))

            fig, ax = subplots()
            ax.plot(self.solar_data_spatial_temporal.variables['time'],mean_solar,color = 'navy')
            ax.set(xlabel='time', ylabel='Solar Radiation (W/m2)',
                title=f'Temporal Variation in Solar Irradiation for {self.location}')
            xticks(rotation=90)
            ax.grid()
            show()


    if any(xy[0][i] != 0 for i in range(len(xy[0]))) or any(xy[1][i] != 0 for i in range(len(xy[1]))):
        fig, ax = subplots()
        ax.plot(xy[0],xy[1],color='#046307')
        ax.set(xlabel=xlabel, ylabel=ylabel,
                title=title)
        if zeroy:
            ax.set_ylim(bottom =0)
        xticks(rotation=90)
        ax.grid()
        show()    
    pass