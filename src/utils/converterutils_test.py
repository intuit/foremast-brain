from utils.converterutils import convertStringToMap, addHeader, convertArrayListToDataFrame,convertStrToInt,convertStrToFloat
from utils.dfUtils import convertToProphetDF,getDataFrame
import pandas as pd


import unittest

class converterutilsMethods(unittest.TestCase):

    
    def testconvertStringToMap(self):
        string = 'error4xx==http://ab683be21d97f11e88e87023426427de-657499332.us-west-2.elb.amazonaws.com:9090/api/v1/query_range?query=namespace_app%3Ahttp_server_requests_error_4xx%7Bnamespace%3D%22default%22%2C+app%3D%22k8s-metrics-demo%22%7D&start=1541035671&end=1541640471&step=60||latency==http://ab683be21d97f11e88e87023426427de-657499332.us-west-2.elb.amazonaws.com:9090/api/v1/query_range?query=namespace_app%3Ahttp_server_requests_latency%7Bnamespace%3D%22default%22%2C+app%3D%22k8s-metrics-demo%22%7D&start=1541035671&end=1541640471&step=60'
        map = convertStringToMap(string," ||", "== ")
    def testAddHeader1(self):
        sample = [1,2,3,4,5,6,7,8,9,10]
        data = addHeader(sample, sample)
        convertToProphetDF(data)
    def testAddHeader2(self):
        sample = [1,2,3,4,5,6,7,8,9,10]
        data = addHeader(sample, sample, sample , isTSIndexOnly=False, tsname='ds', valname='y')
    def testconvertArrayListToDataFrame(self):
        arraylist =[[1,1],[1,1],[1,1],[1,1]]
        convertArrayListToDataFrame(arraylist)
    def testConvertStrToInt(self):
        ret = convertStrToInt('123',0)
    def testConvertStrToFloat(self):
        ret = convertStrToFloat('123.0',0.0)
    def testgetDataFrame(self):
        fds = pd.read_csv('../../test_data/seasonality.csv')
        lstm1, lstm_display1 = getDataFrame(fds, True)  
        lstm2, lstm_display2 = getDataFrame(fds, False)  