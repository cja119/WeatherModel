from numpy import pi, cos
from numpy.random import random, seed
from MeteorologicalScripts.PlotWeatherData import timeseriesplot
from pandas import DataFrame

def interpolate(inp, fi):
            # This function simply interpolates the profile, indexed by the 'number_points' into a  list, indexed by 'number_time_steps':
            
            # Split floating-point index into whole & fractional parts.
            i, f = int(fi // 1), fi % 1  
            # Avoiding an index-related error.
            j = i+1 if f > 0 else i         
            return (1-f) * inp[i] + f * inp[j]

class Demand_profle:
    def __init__(self,number_points,number_time_steps: int = 8760, peak_seasonal_demand: float = 0.25, net_frequency: float= 1,net_ramp: float = 0,baseline: float = 0, net_demand: float = 1, stochasticity: float = 0, amplitude: float = 0):
            '''
            The Demand Profile Class returns a list called Demand_profile.interpolate, which contains a custom demand profile subject to the customisable hyperparameters, 
            which are elucidated below. This code works by calculating a normalised profile, which is then scaled to adhere to a 'net_demand' value accross the entire profile. 

            number_points:          int     -> This is the number of points within the profile itself. This is not to be confused with 'number_time_steps'.
            number_time_steps:      int     -> This is the number of points in the 'interpolate' list, which is interpolated over the whole profile.
            peak_seasonal_demand:   float   -> This is the fraction within the time period at which the peak demand from the oscillatory contribution is to align.
            net_frequency:          float   -> This is the number of complete sinusoidal oscillations that are to occur during the time period.
            net_ramp:               float   -> This is the fraction of the average demand that is to manifest as a linear ramp.
            baseline:               float   -> This is the 'y intercept' of the ramp.
            net_demand:             float   -> This is the overall demand by which the profile is scaled to achieve. 
            stochasticity:          float   -> This is the 'amplitude' of the stochastic factor which occurs at every point (not time step!).
            amplitude:              float   -> This is the amplitude of the sinusoidal oscillation.

            N.B, it seems having fewer points than time steps allows for the stochasticity to have a sufficient amplitude to be representative, but without the profile being
            too 'fuzzy'.

            
            '''
            # Setting a random seed for the stochastic factor. This ensures runs are comparable. 
            seed(42)

            # Generating blank arrays for number of points, which is then interpolated over to give the correct number of time steps of the model, and time steps.
            self.points_list    = list(range(0,number_points))
            time_list           = list(range(0,number_time_steps))
            
            # This determines the total ramp implemented accross the net annual demand. 
            ramp           = [((net_ramp / number_time_steps) * time_list[i] + baseline) for i in range(len(time_list))]
            
            # This implements the sinusoidal osciallation, adjusted such that the custom frequency and the peak seasonal demands are reflected in the profile. 
            amplitude      = amplitude 
            frequency           = 2 * net_frequency * pi / number_time_steps
            oscillatory    = [amplitude * cos(frequency * time_list[i] - peak_seasonal_demand * 2*pi) for i in range(len(time_list))]
            
            # Calculating the stochastic list.
            stochasticity  = random(number_time_steps) * stochasticity 

            # Calculating the pre-scaled, pre-interpolated profile.
            unit_demand    = [(oscillatory[i] + ramp[i]) * (1 + stochasticity[i])  for i in range(len(time_list))]
            
            # Calculating the scale factor by which the unit profile must be scaled.
            total_demand   = (sum([unit_demand[i] for i in range(1, number_time_steps-1)]) + 0.5*(unit_demand[0] + unit_demand[-1])) 
            scale_factor   = net_demand / total_demand
            
            # Scaling the profile and then interpolating to acheive the desired number of steps. 
            demand              = [unit_demand[i] * scale_factor for i in range(len(time_list))]
            delta               = (len(demand)-1) / (number_points)
            self.interpolate    = [interpolate(demand , i*delta) for i in range(0,number_points)]
            pass
    
    
    def generate_plot(self):
        timeseriesplot(self,xy=(self.points_list,self.interpolate),title='Energy Demand against Time', ylabel='Energy Demand (GJ)',xlabel='Time',zeroy=True)
        pass    
