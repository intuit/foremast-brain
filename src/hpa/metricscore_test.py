from hpa.metricscore import hpametricinfo

import unittest


class metriccore_test(unittest.TestCase):
    def testOrder(self):
        hpametrics = [hpametricinfo(5,"latency",100,1),  hpametricinfo(3,"4xx",100,1),
                      hpametricinfo(7,"2xx",100,1),hpametricinfo(1,"tps",100,1)  ]

        hpametric_sorted = sorted(hpametrics)
        hand_sorted_order = [c.priority for c in hpametric_sorted]  
        ll =[]
        for i in range(len(hand_sorted_order)):
            ll.append(hand_sorted_order[i])
        self.assertEqual(ll, [1, 3, 5, 7])
        
if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()               
