from numpy import random, argmax, datetime64, arange, array

def time_sampling(dataset, sample_type: str = "Structured", interval: int = 3600, n_samp: int = 100, graph: bool = False, 
             time_data: tuple[datetime64,datetime64]=(datetime64('2022-07-17T00:30:00.000000000', 'ns'),
                                                      datetime64('2022-07-31T00:30:00.000000000', 'ns'))):
    
    '''This code generates samples at regular intervals for a given xarray dataset and returns an xarray dataset at the required intervals.
    Note, 'interval' is in seconds.
 
    dataset:        xarray.Dataset               -> This is the dataset to be sampled.
    sample_type:    "Structured" or "Random"     -> This is the sampling strategy to be used.
    n_samp:         int                          -> This is the number of samples to be taken.
    graph:          Boolean                      -> This is a graphing specific hyperparameter.
    time_data:      tuple[datetime64,datetime64] -> This is the start and end time. 


    '''

    # Generating the random samples, if the sampling type is random. This returns the randomly sampled list in order of ascending date. 
    if sample_type == "Random":
        random_args = random.randint(0,len(dataset.variables['time']),n_samp)
        random_args.sort()
        return dataset[random_args]

    # Generating the structured samples                          
    elif sample_type == "Structured":

        # Finding the increment of the time data and then checking it is of the right format (timedelta64[ns]).
        scale_factor = dataset.variables['time'][1] - dataset.variables['time'][0]

        if scale_factor.dtype == "timedelta64[ns]":

            # 10000 is the default value, but if this doesn't work, set the time increment to the difference between the first and second datapoint. 
            time_increment  = dataset.variables['time'].attrs['time_increment']
            if time_increment == 10000:
                increment_ns = 3600*10**9
            else:
                increment_ns   = (scale_factor)
                raise Warning("Unknown increment, calculated from first and second datapoint - check accuracy")
        else: 
            raise ValueError("Scale factor is not 'timedelta64[ns]', other datatypes are not currently managable")

        # These are graphing specific values. 
        if graph:
            interval_ns = increment_ns
            begin_time  = time_data[0]
            end_time    = time_data[1]
            n_samp      = int(int(end_time - begin_time) / (increment_ns))
            time_points = array(arange(n_samp)*interval_ns, dtype='int64') + array([[str(begin_time)]*n_samp], dtype = 'datetime64[ns]')
        else:
            # The interpolation constructs the datetime64 string in order to index the dataset correctly via the dataset.interp() function
            interval_ns = interval*10**9
            begin_time  = str(dataset.variables['time'].attrs['begin_time'])
            begin_time  = str((6 - len(begin_time))*'0'+begin_time)
            begin_date  = str(dataset.variables['time'].attrs['begin_date'])
            n_dp        = argmax(dataset.variables['time'].data)
            samp_ratio  = float(interval_ns) / float(increment_ns)
            n_samp      = int(n_dp / samp_ratio) 
            initial     = datetime64(begin_date[0:4]+'-'+begin_date[4:6]+'-'+begin_date[6:8]+'T'+begin_time[0:2]+':'+begin_time[2:4],'ns')
            time_points = array(arange(n_samp)*interval_ns, dtype='int64') + array([[str(initial)]*n_samp], dtype = 'datetime64[ns]')
        return dataset.interp({'time':time_points[0]})
    
    else: 
        raise ValueError("Sampling must be either 'Random' or 'Structured'")              

def geospatial_sampling(dataset, latitudes: tuple[float,float], longitudes: tuple[float,float]):
    
    # Interpolating the dataset geospatially, this is all done by the dataset.sel() function. 
    min_lat     = latitudes[0]
    max_lat     = latitudes[1]
    min_lon     = longitudes[0]
    max_lon     = longitudes[1]
    return dataset.sel(lat=slice(min_lat,max_lat), lon=slice(min_lon,max_lon))