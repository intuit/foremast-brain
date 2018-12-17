from metadata.metadata import METRIC_PERIOD


class MetricInfo:
    def __init__(self, metricClass='MetricInfo'):
        self.metricClass = metricClass


class SingleMetricInfo(MetricInfo):
    def __init__(self, metricName, metricKeys, columnmap, metricDF, metricTCategory=METRIC_PERIOD.CURRENT.value,
                 metricClass='SingleMetricInfo'):
        super().__init__(metricClass)
        self.columnmap = columnmap
        self.metricDF = metricDF
        self.metricName = metricName
        self.metricKeys = metricKeys
        self.metricTCategory = metricTCategory


class MultiTypeMetricInfo(MetricInfo):
    def __init__(self, metricNamelist, metricKeys, columnmap, metricDF, metricTCategorylist,
                 metricClass='MultiTypeMetricInfo'):
        super().__init__(metricClass)
        self.columnmap = columnmap
        self.metricNamelist = metricNamelist
        self.metricKeys = metricKeys
        self.metricDF = metricDF
        self.metricTCategorylist = metricTCategorylist


class MultiKeyMetricInfo(MetricInfo):
    def __init__(self, metricName, metricKeyslist, columnmap, metricDF, metricTCategorylist,
                 metricClass='MultiKeyMetricInfo'):
        super().__init__(metricClass)
        self.columnmap = columnmap
        self.metricName = metricName
        self.metricKeyslist = metricKeyslist
        self.metricDF = metricDF
        self.metricTCategorylist = metricTCategorylist
