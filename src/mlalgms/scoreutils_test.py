from mlalgms.scoreutils import convertToZscore, convertToPvalue



        
print(convertToZscore(0.8))
print(convertToPvalue(0.8416212335729143))   


import unittest

class scoreutilsMethods(unittest.TestCase):

    
    def testconvertToZscore(self):
        ret = convertToZscore(0.8)
        self.assertEqual(ret, 0.8416212335729143)
    def testconvertToPvalue(self):
        ret = convertToPvalue(0.8416212335729143)
        self.assertEqual(ret, 0.8)

if __name__ == '__main__':
    unittest.main()
        