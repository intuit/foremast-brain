import sys
sys.path.append('../')
from metadata.metadata import METRIC_PERIOD


class ModelHolder:
    def __init__(self, modelname, modelconfig=None, modeldata=None, period = METRIC_PERIOD.HISTORICAL.value, id=''):
        if modelconfig is None:
            modelconfig = {}
        if modeldata is None:
            modeldata = {}
        self.modelname = modelname
        self.modeldata = modeldata
        self.period = period
        self.modelconfig = modelconfig
        self._id = id

    def getModelByKey(self, key):
        return self.modeldata.get(key)

    def setModelKV(self, key, value):
        self.modeldata.setdefault(key, value) 

    def hasModel(self):
        return len(self.modeldata)>0

    def getModelConfigByKey(self, key):
        return self.modelconfig.get(key)

    def setModelConfig(self, key ,value):
        self.modelconfig.setdefault(key,value)

    def setModelName(self, name):
        self.modelname = name

    def resetModel(self, data):
        self.modeldata = data

    def setModelMetadata(self, metadata):
        self.metadata = metadata

    @property
    def id(self):
        return self._id

    def __getitem__(self, item):
        return self.getModelByKey(item)

    def __setitem__(self, key, value):
        self.setModelKV(key, value)

    def __str__(self):
        sb = []
        sb.append('modelname: ')
        sb.append(self.modelname)
        sb.append(', modedata: ')
        sb.append(str(self.modeldata))
        sb.append(', modelconfig: ')
        sb.append(str(self.modelconfig))
        sb.append(', period: ')
        sb.append(self.period)
        return ''.join(sb)

    



        
        

