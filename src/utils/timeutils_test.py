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
   