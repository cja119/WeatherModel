# Python-Meteor [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3124/)  [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14678366.svg)](https://doi.org/10.5281/zenodo.14678366)
These functions are used repeatedly accross many different repositories for my research. I keep them updated, so figured it would be best to keep the repository in one location (rather than repeating the files accross many repositories) such that they can be updated unilaterally. 
<p align="center">
  <img src="png/meteor_logo.png" alt="Centered Image" width="400"/>
</p>


## Quick Start 

First, clone the repository to your local system:
```
git clone https://github.com/cja119/meteor_py.git
````
Then, install all the package!
```
pip install -e meteor_py
```
Running the python function 'WeatherData' will grab the weatherdata files from the NASA Merra-2 database [1]. This is achieved using the [EarthAccess Library](https://earthaccess.readthedocs.io/en/latest/) (N.B., this will require an [EarthData](https://urs.earthdata.nasa.gov/) account, with 'NASA GESDISC DATA ARCHIVE' activated under the applications tab). Once set up, save your username and password as environment variables using the following shell commands:
```
export EARTHDATA_USERNAME="Your_Username"

export EARTHDATA_PASSWORD="Your_Password"
```


