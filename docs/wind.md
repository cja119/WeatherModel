# Wind Model

The wind farm for this model is a Vestas 3.3 MW turbine, with a slightly extended cutoff speed of 30m/s. The wind speed at the hub height (100m) is modelled using a hellman exponant of 0.15, with the following equaiton:

$$
v(h,v_{H_0}(t)) = v_{H=H_0}(t) \times \left(\frac{H_{hub}}{H_0}\right)^{0.15}
$$

This wind speed is then input into the provided power curve and subsequently interpolated to derive a weather profile:

$$
P_{turb}= f(v(h,v_{H_0}(t)))
$$

For the wind data, due to the long term nature of weather patterns, it is optional to apply Ward's method of heirarchical clustering by setting the boolean parameter 'cluster' to True when initialising the RenewableEnergy Module. 
