
import unittest 

from helpers.hpahelpers import retrieveConfig ,calculateHPAModels
from helpers.envparameters import envparameters
from models.modelclass import ModelHolder
from metadata.metadata import REQUEST_STATE,METRIC_PERIOD
from metadata.metadata import THRESHOLD, LOWER_THRESHOLD, BOUND,MIN_LOWER_BOUND
from metadata.metadata import REQUEST_STATE,METRIC_PERIOD, MIN_DATA_POINTS

class foremastbrainhelperMethods(unittest.TestCase):
    envs = envparameters()
    def testretrieveConfig(self):
      modelConfig = {THRESHOLD: self.envs.ML_THRESHOLD, LOWER_THRESHOLD: self.envs.ML_LOWER_THRESHOLD,
                                   MIN_DATA_POINTS: self.envs.min_historical_data_points, BOUND: self.envs.ML_BOUND, 
                                   MIN_LOWER_BOUND: self.envs.ML_MIN_LOWER_BOUND}  
      modelHolder = ModelHolder(self.envs.ML_ALGORITHM, modelConfig ,{"type1":{THRESHOLD: self.envs.ML_THRESHOLD,
                                                   LOWER_THRESHOLD: self.envs.ML_LOWER_THRESHOLD,
                                                    MIN_LOWER_BOUND: self.envs.ML_MIN_LOWER_BOUND}}, METRIC_PERIOD.HISTORICAL.value, "1234")
      threshold, lowerthreshold, minLowerBound = retrieveConfig("type1", modelHolder)
      print(threshold, lowerthreshold, minLowerBound )
      

 #   def testcalculateHPAModels(self):
 #       calculateHPAModels(None, None, None)



if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()   
         