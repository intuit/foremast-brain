
from prometheus_client import Gauge 

metric_prefix = "foremastbrain:"

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
        metricNameUpper = metric_prefix+metricname+"_upper"
        metricNameLower = metric_prefix+metricname+"_lower"
      
        if not (metricNameUpper in self.instance.metrics ):
            self.instance.metrics[metricNameUpper] = Gauge(metricNameUpper, metricNameUpper+" model upper bound",
                                                           labelnames=labels.keys())
        if not (metricNameLower in self.instance.metrics ):
            self.instance.metrics[metricNameLower] = Gauge(metricNameLower, metricNameLower+" model upper bound", 
                                                           labelnames=labels.keys())                                      
                                                   
    def sendMetric(self,metricname, labeldata, value, isUpper = True):
        newMetricName = metric_prefix+metricname
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
        newMetricName = metric_prefix+metricname
        if not (newMetricName in self.instance.metrics ):
            self.instance.metrics[newMetricName] = Gauge(newMetricName, newMetricName+" measurement metric",
                                                           labelnames=labels.keys())                                                                                    
    def sendMetric(self,metricname, labeldata, value):
        newMetricName = metric_prefix+metricname
        if not (newMetricName in self.instance.metrics) :
            self.setMetricInfo(metricname, labeldata) 
        self.instance.metrics[newMetricName].labels(**labeldata).set(value)



    
    
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
        metricNameAnomaly = metric_prefix+metricname+"_anomaly"
        if not (metricNameAnomaly in self.instance.metrics ):
            self.instance.metrics[metricNameAnomaly] = Gauge(metricNameAnomaly, metricNameAnomaly+" anomaly timestamp",  
                    labelnames=labels.keys())                                                                                        
                                                   
    def sendMetric(self,metricname, labeldata, value):
        newMetricName  = metric_prefix+metricname+"_anomaly"
        if not (newMetricName in self.instance.metrics ):
            self.setMetricInfo(metricname, labeldata)            
        self.instance.metrics[newMetricName].labels(**labeldata).set(value)