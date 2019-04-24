class globalconfig:
    class __globalconfig:
        def __init__(self):
            self.configs = {}
            self.thresholds ={}
        def __str__(self):
            return repr(self) + self.configs + self.thresholds
    instance = None
    def __init__(self):
        if not globalconfig.instance:
            globalconfig.instance = globalconfig.__globalconfig()
    def setKV(self, key, value):
        self.instance.configs[key] = value
    def getValueByKey(self,key, defaultValue = None):
        if not ( key in self.instance.configs.keys()):
            return defaultValue
        return self.instance.configs[key]
    def getKVs(self):
        return self.instance.configs
    
    def getThresholdByKey(self, metricType, key):
        if not ( metricType in self.instance.thresholds ):
            return self.instance.configs[key]
        return self.instance.thresholds[metricType][key]

    def setThresholdKV(self, metricType, key, value):
        if not ( metricType in self.instance.thresholds ):
            self.instance.thresholds[metricType]={}
        self.instance.thresholds[metricType][key]=value
        
        
        
        

    
    
    
    


   
