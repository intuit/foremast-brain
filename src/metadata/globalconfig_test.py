from metadata.globalconfig import globalconfig
import unittest


class globalconfig_test(unittest.TestCase):

 def testSetKV(self):   
    x =  globalconfig()
    x.setKV('a',1)
    x.setKV('b', 3) 
    y = globalconfig()
    y.setKV('dd',4)
    result = {'a': 1, 'b': 3, 'dd': 4}
    self.assertEqual(y.getKVs(), result)
    
    data =x.getValueByKey('a', defaultValue = "aa")
    data1 = x.getKVs()
    data2 = x.getThresholdByKey("a","a")
    data3 = x.setThresholdKV("a","a","value")
    
    
    
if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()        
    
