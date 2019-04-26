
from metadata.metadata import METRIC_PERIOD
from datetime import datetime, timezone

class ModelHolder:
    def __init__(self, model_name, model_config=None, model_data=None, period=METRIC_PERIOD.HISTORICAL.value, id=''):
        #nest dict
        if model_config is None:
            model_config = {}
        if model_data is None:
            model_data = {}
        self._model_name = model_name
        self._model_data = model_data
        self._period = period
        self._model_config = model_config
        self._id = id
        self._timestamp = str(datetime.now(timezone.utc).astimezone())

    '''
    def getModelByKey(self, key):
        return self._model_data.get(key)

    def setModelKV(self, key, value):
        self._model_data.setdefault(key, value)
    '''
    def getModelByKey(self, metricType, key):
        if not metricType in self._model_data:
            return None
        return self._model_data[metricType][key]

    def setModelKV(self, metricType, key, value):
        if not ( metricType in self._model_data ):
            self._model_data[metricType]={}
        self._model_data[metricType][key]=value

    def getModelConfigKeys(self):
        return self._model_config.keys()
    
    def getMapByMetricType(self, metricType):
        if not metricType in self._model_data:
            return None
        return self._model_data[metricType]
    
    def getModelConfigByKey(self, key1, key2=None, key3=None):
        if key2 is None:
            return self.getModelConfigByKey1(key1)
        else:
            if key3 is None:
                return self.getModelConfigByKey2(key1,key2)
            else:
                return self.getModelConfigByKey3(key1,key2, key3)
    

    def getModelConfigByKey1(self, key1):
        if not key1 in self._model_config:
            return None
        return self._model_config[key1]
    
    def getModelConfigByKey2(self, key1, key2):
        if not key1 in self._model_config:
            return None
        if not key2 in self._model_config[key1]:
            return None
        return self._model_config[key1][key2]
        
    
    def setModelConfig(self,key, data1, data2=None, data3 =None):
        if data2 is None : 
            return self.setModelConfig1(key,data1)
        else:
            if data3 is None :
                self.setModelConfig2(key,data1, data2)
            else:
                self.setModelConfig3(key, data1, data2, data3)

    
    def setModelConfig1(self,key,data1):
        if not ( key in self._model_config):
            self._model_config[key]={}
        self._model_config[key] = data1
        
    def setModelConfig2(self,key, data1, data2):
        if not ( key in self._model_config):
            self._model_config[key]={}
        if not (data1 in self._model_config[key] ):
            self._model_config[key][data1]={}
        self._model_config[key][data1]= data2
        
    def setModelConfig3(self,key, data1, data2, data3):
        if not ( key in self._model_config):
            self._model_config[key]={}
        if not (data1 in self._model_config[key] ):
            self._model_config[key][data1]={}
        if not (data2 in self._model_config[key][data1] ):
            self._model_config[key][data1][data2]={}    
        self._model_config[key][data1][data2]= data3


    @property
    def period(self):
        return self._period

    @property
    def model_name(self):
        return self._model_name
    '''
    @property
    def hasModel(self):
        return len(self._model_data) > 0
    '''
    @property
    def hasModels(self):
        return len(self._model_data) > 0

    @property
    def hasModel(self, metricType):
        return len(self._model_data[metricType]) > 0


    @property
    def id(self):
        return self._id

    @property
    def timestamp(self):
        return self._timestamp

#    def __getitem__(self, metricType, item):
#        return self.getModelByKey(metricType, item)

#   def __setitem__(self, metricType,key, value):
#       self.setModelKV(metricType, key, value)

    def __str__(self):
        sb = []
        sb.append('model_name: ')
        sb.append(self.model_name)
        sb.append(', modeldata: ')
        sb.append(str(self._model_data))
        sb.append(', modelconfig: ')
        sb.append(str(self._model_config))
        sb.append(', period: ')
        sb.append(self.period)
        return ''.join(sb)
