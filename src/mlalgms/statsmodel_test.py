from mlalgms.statsmodel import calculateTSTrend
import unittest

class statModelMethods(unittest.TestCase):

    
    def testcalculateTSTrend(self):
        test_data = [1,100,20,49.5]
        ret = calculateTSTrend(test_data) 
        self.assertEqual(ret, -0.006798396408786019)

if __name__ == '__main__':
    unittest.main()
        

    