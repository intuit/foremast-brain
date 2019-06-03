import unittest
from metadata.metadata import REQUEST_STATE

class metadata_test(unittest.TestCase):
    ww= REQUEST_STATE.COMPLETED_HEALTH
    ##Test ##   
    def testState(self):
        expected = REQUEST_STATE.COMPLETED_HEALTH
        self.assertEqual(self.ww, expected)
        
        
if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()        
