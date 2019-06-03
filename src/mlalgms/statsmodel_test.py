from mlalgms.statsmodel import calculateTSTrend
import unittest

class statModelMethods(unittest.TestCase):

    
    def testcalculateTSTrend(self):
        test_data = [1,100,20,49.5]
        ret = calculateTSTrend(test_data) 
        self.assertEqual(ret, -0.006798396408786019)
    def testcalculateTSTrend2(self):
        test_data = [1,100,20,49.5]
        test_data2 = [1,3,5,7,9]
        ret = calculateTSTrend(test_data, test_data2) 
        self.assertEqual(ret, -0.013596792817572038)

if __name__ == '__main__':
    unittest.main()
        
