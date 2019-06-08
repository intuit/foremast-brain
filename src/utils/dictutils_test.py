from utils.dictutils import *


import unittest


class dictutilsMethods(unittest.TestCase):#TODO: 
    def testRetrieveKVList(self):
        data ={'a':1,'b':2}
        k,v =retrieveKVList(data)
    def testConvertDictKey(self):
        data ={'a':1,'b':2}
        convertDictKey(data,'a','c')
        
        
if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()            