from utils.timeutils import *
from dateutil.parser import parse

import unittest

class timeutilsMethods(unittest.TestCase):
    def testgetNowInSeconds(self):
        getNowInSeconds()
    def testgetNow(self):
        getNow()

    def testgetNowStr(self):
        getNowStr()
   
   
   
if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()    