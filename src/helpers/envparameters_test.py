import unittest 

from helpers.envparameters import envparameters


class envparametersMethods(unittest.TestCase):
    envs = envparameters()
    def testrunenvtests(self):
        self.envs.min_historical_data_points
        self.envs.ML_PROPHET_FREQ
        self.envs.ML_PROPHET_PERIOD
        self.envs.metric_threshold_count
        self.envs.ML_ALGORITHM
        self.envs.ML_LOWER_THRESHOLD
        self.envs.FOREMAST_SERVICE_URL
        self.envs.CURRENT_CONF_POD_TIME_WINDOW
        self.envs.HISTORICAL_CONF_TIME_WINDOW
        self.envs.CURRENT_CONF_TIME_WINDOW
        self.envs.ML_BOUND
        self.envs.ML_MIN_LOWER_BOUND


    
    
        
if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()   
         
    