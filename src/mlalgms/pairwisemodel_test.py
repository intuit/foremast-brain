from numpy.random import randn

from mlalgms.pairwisemodel import TwoDataSetSameDistribution,DEFAULT_PAIRWISE_THRESHOLD,ANY
from mlalgms.statsmodel import IS_UPPER_BOUND

import unittest

class pairwisemodelMethods(unittest.TestCase):

    
    def testTwoDataSetSameDistribution(self):
        data1 = 5 * randn(100) + 50
        data2 = 5 * randn(100) + 51
        ret,  p, _,  _ = TwoDataSetSameDistribution(data1, data2, 
                                   alpha=DEFAULT_PAIRWISE_THRESHOLD, algorithm=ANY, bound= IS_UPPER_BOUND) 
        self.assertEqual(ret, True)

if __name__ == '__main__':
    unittest.main()