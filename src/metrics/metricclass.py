from metadata.metadata import METRIC_PERIOD


class MetricInfo:
    def __init__(self, metricClass='MetricInfo'):
        self.metricClass = metricClass


class SingleMetricInfo(MetricInfo):
    def __init__(self, metricName, metricKeys, columnmap, metricDF, metricTCategory=METRIC_PERIOD.CURRENT.value,
                 metricClass='SingleMetricInfo'):
        self.columnmap = columnmap
        self.metricDF = metricDF
        self.metricName = metricName
        self.metricKeys = metricKeys
        self.metricTCategory = metricTCategory
        self.metricClass = metricClass


class MultiTypeMetricInfo(MetricInfo):
    def __init__(self, metricNamelist, metricKeys, columnmap, metricDF, metricTCategorylist,
                 metricClass='MultiTypeMetricInfo'):
        self.columnmap = columnmap
        self.metricNamelist = metricNamelist
        self.metricKeys = metricKeys
        self.metricDF = metricDF
        self.metricTCategorylist = metricTCategorylist
        self.metricClass = metricClass


class MultiKeyMetricInfo(MetricInfo):
    def __init__(self, metricName, metricKeyslist, columnmap, metricDF, metricTCategorylist,
                 metricClass='MultiKeyMetricInfo'):
        self.columnmap = columnmap
        self.metricName = metricName
        self.metricKeyslist = metricKeyslist
        self.metricDF = metricDF
        self.metricTCategorylist = metricTCategorylist
        self.metricClass = metricClass
