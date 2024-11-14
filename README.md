# Renewable Energy Systems Model

These functions are used repeatedly accross many different repositories for my research. I keep them updated, so figured it would be best to keep the repository in one location (rather than repeating the files accross many repositories) such that they can be updated unilaterally. 

## Weather Data and TimeSeries Clustering
Running the python scripts 'GetWeatherData.py' will grab the weatherdata files from the NASA Merra-2 database. This is achieved using the [EarthAccess Library](https://earthaccess.readthedocs.io/en/latest/) (N.B., this will require an [EarthData](https://urs.earthdata.nasa.gov/) account, with 'NASA GESDISC DATA ARCHIVE' activated under the applications tab). Once set up, save your username and password as environment variables using the following shell commands:
```
export EARTHDATA_USERNAME="Your_Username"
```

```
export EARTHDATA_PASSWORD="Your_Password"
```
The python file 'ClusterWeatherData.py' can then be used to generate the Culsters using Ward's method. N.B., this will override the default clustered datasets saved in the abovementioned csv files. 

## Sample Weather Data

<p align="center">
  <img src="image.png" alt="Centered Image" width="900"/>
</p>
