import numpy as np




"""
#moving avg 
#Parameters
    array of ts value
#Returns moving avg
"""
def moving_average(series, n):
    return np.average(series[-n:])



#exponential_smoothing(df, 0.25)
#usually the oldes take less weightage 
'''
def exponential_smoothing(values, alpha):
    result = [values.iloc[0]] # first value is same as series
    for n in range(1, len(values)):
            result.append(alpha * values.iloc[n] + (1 - alpha) * result[n-1])    
    return result
'''
def exponential_smoothing(series, alpha):
    result = [series[0]] # first value is same as series
    for n in range(1, len(series)):
        result.append(alpha * series[n] + (1 - alpha) * result[n-1])
    return result

# l_x = a*y_x +(1-a)* (l_(x-1)+b_(x-1))
# b_x = beta*(l_x - l_(x-1))+ (1-beta)*b_(x-1) 
#yhat_(x+1)= l_x+b_x
#double_exponential_smoothing(ads.Ads, alphas=[0.9, 0.02], betas=[0.9, 0.02])
def double_exponential_smoothing(values, alpha, beta):
    """
    #Parameters:
        series: dataset with timeseries
        alpha:  float [0.0, 1.0], smoothing parameter for level
        beta:   float [0.0, 1.0], smoothing parameter for trend
        
    #Returns:
        restult: calculated double exponential smoothing dagasset
    """
    # first value is same as series
    result = [values[0]]
    for n in range(1, len(values)):
        if n == 1:
            level, trend = values[0], values[1] - values[0]
        if n >= len(values): # forecasting
            value = result[-1]
        else:
            value = values[n]
        last_level, level = level, alpha*value + (1-alpha)*(level+trend)
        trend = beta*(level-last_level) + (1-beta)*trend
        result.append(level+trend)
    return result




#use defined for small data set only (last n of weights size)
#weighted_average(series, [0.7, 0.2, 0.1])
# this is not used very often, only apple to small dataset
#it's better weights size <= series size
def weighted_average(series, weights):
    """
        Calculate weighter average on series
    """
    result = 0.0
    weights.reverse()
    for n in range(len(weights)):
        result += series.iloc[-n-1] * weights[n]
    return float(result)
