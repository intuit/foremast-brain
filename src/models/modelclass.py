import sys

sys.path.append('../')
from metadata.metadata import METRIC_PERIOD


class ModelHolder:
    def __init__(self, model_name, model_config=None, model_data=None, period=METRIC_PERIOD.HISTORICAL.value, id=''):
        if model_config is None:
            model_config = {}
        if model_data is None:
            model_data = {}
        self._model_name = model_name
        self._model_data = model_data
        self._period = period
        self._model_config = model_config
        self._id = id

    def getModelByKey(self, key):
        return self._model_data.get(key)

    def setModelKV(self, key, value):
        self._model_data.setdefault(key, value)

    def getModelConfigByKey(self, key):
        return self._model_config.get(key)

    @property
    def period(self):
        return self._period

    @property
    def model_name(self):
        return self._model_name

    @property
    def hasModel(self):
        return len(self._model_data) > 0

    @property
    def id(self):
        return self._id

    def __getitem__(self, item):
        return self.getModelByKey(item)

    def __setitem__(self, key, value):
        self.setModelKV(key, value)

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
