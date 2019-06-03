from mlalgms.scoreutils import convertToZscore, convertToPvalue



import unittest

class scoreutilsMethods(unittest.TestCase):

    
    def testconvertToZscore(self):
        ret = convertToZscore(0.8)
        self.assertEqual(ret, 0.8416212335729143)
        ret = convertToZscore(0.85)
        self.assertEqual(ret, 1.0364333894937898)
        ret = convertToZscore(0.75)
        self.assertEqual(ret, 0.6744897501960817)
    def testconvertToPvalue(self):
        ret = convertToPvalue(0.8416212335729143)
        self.assertEqual(ret, 0.8)

if __name__ == '__main__':
    unittest.main()
        
