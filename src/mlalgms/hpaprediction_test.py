import unittest
import pandas as pd
from utils.dfUtils import getDataFrame
from mlalgms.hpaprediction import calculateHistoricalModel,checkAnomaly
from metadata.metadata import AI_MODEL


class HPAPredictionMethods(unittest.TestCase):
    
    def testalgm(self):
        fds = pd.read_csv('../../test_data/fds_seasonality.csv')
        lstm, lstm_display = getDataFrame(fds, True)  
        modelType, otherdata = calculateHistoricalModel(lstm)
        if modelType in [AI_MODEL.MOVING_AVERAGE_ALL.value]:
            assert otherdata is not None
        elif modelType in [AI_MODEL.PROPHET.value]:
            assert otherdata is not None
            timestamp = 1553280300.0
            value = 500    
            ret = checkAnomaly(timestamp, value, otherdata) 
            self.assertEqual(ret, 0)

if __name__ == '__main__':
    unittest.main()

       
