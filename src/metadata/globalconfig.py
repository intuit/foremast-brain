class globalconfig:
    class __globalconfig:
        def __init__(self):
            self.configs = {}
        def __str__(self):
            return repr(self) + self.configs
    instance = None
    def __init__(self):
        if not globalconfig.instance:
            globalconfig.instance = globalconfig.__globalconfig()
    def setKV(self, key, value):
        self.instance.configs[key] = value
    def getValueByKey(self,key):
        return self.instance.configs[key]
    def getKVs(self):
        return self.instance.configs
    
    
    


   