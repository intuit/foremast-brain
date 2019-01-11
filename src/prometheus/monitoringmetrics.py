
from prometheus_client import Gauge 

class modelmetrics:
    class __modelmetrics:
        def __init__(self):
            self.metrics = {}
        def __str__(self):
            return repr(self) + self.configs
    instance = None
    def __init__(self):
        if not modelmetrics.instance:
            modelmetrics.instance = modelmetrics.__modelmetrics()
    def setMetricInfo(self, metricname, labels):
        metricNameUpper = metricname+"_upper"
        metricNameLower = metricname+"_lower"
      
        if not (metricNameUpper in self.instance.metrics ):
            self.instance.metrics[metricNameUpper] = Gauge(metricNameUpper, metricNameUpper+" model upper bound",
                                                           labelnames=labels.keys())
        if not (metricNameLower in self.instance.metrics ):
            self.instance.metrics[metricNameLower] = Gauge(metricNameLower, metricNameLower+" model upper bound", 
                                                           labelnames=labels.keys())                                      
                                                   
    def sendMetric(self,metricname, labeldata, value, isUpper = True):
        newMetricName = metricname
        if isUpper:
            newMetricName  += "_upper"
        else:
            newMetricName  += "_lower"
        if not (newMetricName in self.instance.metrics) :
            self.setMetricInfo(metricname, labeldata) 
        self.instance.metrics[newMetricName].labels(**labeldata).set(value)






class measurementmetrics:
    class __measurementmetrics:
        def __init__(self):
            self.metrics = {}
        def __str__(self):
            return repr(self) + self.configs
    instance = None
    def __init__(self):
        if not measurementmetrics.instance:
            measurementmetrics.instance = measurementmetrics.__measurementmetrics()
    def setMetricInfo(self, metricname, labels):
        if not (metricname in self.instance.metrics ):
            self.instance.metrics[metricname] = Gauge(metricname, metricname+" measurement metric",
                                                           labelnames=labels.keys())                                                                                    
    def sendMetric(self,metricname, labeldata, value):
        if not (metricname in self.instance.metrics) :
            self.setMetricInfo(metricname, labeldata) 
        self.instance.metrics[metricname].labels(**labeldata).set(value)



    
    
class anomalymetrics:
    class __anomalymetrics:
        def __init__(self):
            self.metrics = {}
        def __str__(self):
            return repr(self) + self.configs
    instance = None
    def __init__(self):
        if not anomalymetrics.instance:
            anomalymetrics.instance = anomalymetrics.__anomalymetrics()
    def setMetricInfo(self, metricname, labels):
        metricNameAnomaly = metricname+"_anomaly"
        if not (metricNameAnomaly in self.instance.metrics ):
            self.instance.metrics[metricNameAnomaly] = Gauge(metricNameAnomaly, metricNameAnomaly+" anomaly timestamp",  
                    labelnames=labels.keys())                                                                                        
                                                   
    def sendMetric(self,metricname, labeldata, value):
        newMetricName  = metricname+"_anomaly"
        if not (newMetricName in self.instance.metrics ):
            self.setMetricInfo(metricname, labeldata)            
        self.instance.metrics[newMetricName].labels(**labeldata).set(value)