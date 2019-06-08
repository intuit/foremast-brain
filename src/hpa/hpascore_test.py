from hpa.hpascore import getIncreaseUnit, logReason, calculateCurrentZscore


import unittest


class hpa_test(unittest.TestCase):
    def testgetIncreaseUnit(self):
        val =     getIncreaseUnit(5, 10)
        self.assertEqual(val, 50)
    def testlogReason(self):
        self.assertEqual(logReason(50),None)
        self.assertEqual(logReason(51),'hpa is scaling up')
        self.assertEqual(logReason(49), 'hpa is scaling down')
    def testcalculateCurrentZscore(self):
        self.assertEqual(calculateCurrentZscore(1,2,2),-0.5)

        
if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()               