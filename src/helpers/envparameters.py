import logging
import os

# logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('aiformast')

from metadata.globalconfig import globalconfig

from metadata.metadata import AI_MODEL
#from metadata.metadata import THRESHOLD, LOWER_THRESHOLD, BOUND, MIN_LOWER_BOUND
from mlalgms.fbprophetalgm import PROPHET_PERIOD, PROPHET_FREQ, DEFAULT_PROPHET_PERIOD, DEFAULT_PROPHET_FREQ
from mlalgms.pairwisemodel import MANN_WHITE_MIN_DATA_POINT
from mlalgms.statsmodel import IS_UPPER_BOUND

from utils.converterutils import convertStrToInt, convertStrToFloat

from metadata.metadata import THRESHOLD, LOWER_THRESHOLD, BOUND,MIN_LOWER_BOUND
from metadata.metadata import DEFAULT_MIN_LOWER_BOUND

METRIC_TYPE_THRESHOLD_COUNT = "metric_type_threshold_count"
METRIC_TYPE = 'metric_type'
DEFAULT_MIN_HISTORICAL_DATA_POINT_TO_MEASURE = 1

config = globalconfig()

class envparameters:
    def __init__(self):
        # Default Parameters can be overwrite by environments
        #max_cache = convertStrToInt(os.environ.get("MAX_CACHE_SIZE", str(MAX_CACHE_SIZE)), MAX_CACHE_SIZE)
        _ML_ALGORITHM = os.environ.get('ML_ALGORITHM', AI_MODEL.MOVING_AVERAGE_ALL.value)
        #this is wavefront parameter
        FLUSH_FREQUENCY = os.environ.get('FLUSH_FREQUENCY', 5)
        OIM_BUCKET = os.environ.get("OIM_BUCKET")
    
        # get historical time window
        _HISTORICAL_CONF_TIME_WINDOW = os.environ.get('HISTORICAL_CONF_TIME_WINDOW', 7 * 24 * 60 * 60)
        _CURRENT_CONF_TIME_WINDOW = os.environ.get('CURRENT_CONF_TIME_WINDOW', 1.75)
        _CURRENT_CONF_POD_TIME_WINDOW = os.environ.get('CURRENT_CONF_TIME_WINDOW', 5.75)
        #this is foremast-service url
        _FOREMAST_SERVICE_URL=   os.environ.get('FOREMAST_SERVICE_URL', "http://localhost:8099/api/v1/getrequest")  
        
        #this is mainly pairwised algorithm.
        MIN_MANN_WHITE_DATA_POINTS = convertStrToInt(
            os.environ.get("MIN_MANN_WHITE_DATA_POINTS", str(MANN_WHITE_MIN_DATA_POINT)), MANN_WHITE_MIN_DATA_POINT)
        #MIN_WILCOXON_DATA_POINTS = convertStrToInt(
        #    os.environ.get("MIN_WILCOXON_DATA_POINTS", str(WILCOXON_MIN_DATA_POINTS)), WILCOXON_MIN_DATA_POINTS)
        #MIN_KRUSKAL_DATA_POINTS = convertStrToInt(os.environ.get("MIN_KRUSKAL_DATA_POINTS", str(KRUSKAL_MIN_DATA_POINTS)),
        #                                          KRUSKAL_MIN_DATA_POINTS)
        
        #ML_THRESHOLD = convertStrToFloat(os.environ.get(THRESHOLD, str(DEFAULT_THRESHOLD)), DEFAULT_THRESHOLD)
        # lower threshold is for warning.
        #ML_LOWER_THRESHOLD = convertStrToFloat(os.environ.get(LOWER_THRESHOLD, str(DEFAULT_LOWER_THRESHOLD)),
        #                                       DEFAULT_LOWER_THRESHOLD)
        _ML_THRESHOLD = convertStrToFloat(os.environ.get(THRESHOLD, str(0.8416212335729143)), 0.8416212335729143)
        _ML_LOWER_THRESHOLD = convertStrToFloat(os.environ.get(LOWER_THRESHOLD, str(0.6744897501960817)), 0.6744897501960817)
        
        _ML_BOUND = convertStrToInt(os.environ.get(BOUND, str(IS_UPPER_BOUND)), IS_UPPER_BOUND)
        _ML_MIN_LOWER_BOUND = convertStrToFloat(os.environ.get(MIN_LOWER_BOUND, str(DEFAULT_MIN_LOWER_BOUND)),
                                               DEFAULT_MIN_LOWER_BOUND)
        # this is for pairwise algorithem which is used for canary deployment anomaly detetion.
        config.setKV("MIN_MANN_WHITE_DATA_POINTS", MIN_MANN_WHITE_DATA_POINTS)
        #config.setKV("MIN_WILCOXON_DATA_POINTS", MIN_WILCOXON_DATA_POINTS)
        #config.setKV("MIN_KRUSKAL_DATA_POINTS", MIN_KRUSKAL_DATA_POINTS)
        config.setKV(THRESHOLD, _ML_THRESHOLD)
        config.setKV(BOUND, _ML_BOUND)
        config.setKV(MIN_LOWER_BOUND, _ML_MIN_LOWER_BOUND)
        
        config.setKV("FLUSH_FREQUENCY", int(FLUSH_FREQUENCY))
        config.setKV("OIM_BUCKET", OIM_BUCKET)
        config.setKV("CACHE_EXPIRE_TIME", os.environ.get('CACHE_EXPIRE_TIME', 30 * 60))
        #config.setKV("REQ_CHECK_INTERVAL", int(os.environ.get('REQ_CHECK_INTERVAL', 45)))
        # Add Metric source env
        
        config.setKV("SOURCE_ENV", "ppd")
        MODE_DROP_ANOMALY = os.environ.get('MODE_DROP_ANOMALY', 'y')
        config.setKV('MODE_DROP_ANOMALY', MODE_DROP_ANOMALY)
        
        
        NO_MATCH_PICK_LAST  = os.environ.get('NO_MATCH_PICK_LAST', 'y')
        config.setKV('NO_MATCH_PICK_LAST', NO_MATCH_PICK_LAST)
        
        wavefrontEndpoint = os.environ.get('WAVEFRONT_ENDPOINT')
        wavefrontToken = os.environ.get('WAVEFRONT_TOKEN')
    
        foremastEnv = os.environ.get("FOREMAST_ENV", 'qa')
        metricDestation = os.environ.get('METRIC_DESTINATION', "prometheus")
        if wavefrontEndpoint is not None:
            config.setKV('WAVEFRONT_ENDPOINT', wavefrontEndpoint)
        else:
            logger.error(
                "WAVEFRONT_ENDPOINT is null!!! foremat-brain will throw exception is you consumer wavefront metric...")
        if wavefrontToken is not None:
            config.setKV('WAVEFRONT_TOKEN', wavefrontToken)
        else:
            logger.error(
                "WAVEFRONT_TOKEN is null!!! foremat-brain will throw exception is you consumer wavefront metric...")
        
        if metricDestation is not None:
            config.setKV('METRIC_DESTINATION', metricDestation)
        else:
            config.setKV('METRIC_DESTINATION', "prometheus")
        if foremastEnv is None or foremastEnv == '':
            config.setKV("FOREMAST_ENV", 'qa')
        else:
            config.setKV("FOREMAST_ENV", foremastEnv)
    
        _metric_threshold_count = convertStrToInt(os.environ.get(METRIC_TYPE_THRESHOLD_COUNT, -1),
                                                 METRIC_TYPE_THRESHOLD_COUNT)
        if _metric_threshold_count >= 0:
            for i in range(_metric_threshold_count):
                istr = str(i)
                mtype = os.environ.get(METRIC_TYPE + istr, '')
                if mtype != '':
                    mthreshold = convertStrToFloat(os.environ.get(THRESHOLD + istr, str(_ML_THRESHOLD)), _ML_THRESHOLD)
                    mbound = convertStrToInt(os.environ.get(BOUND + istr, str(_ML_BOUND)), _ML_BOUND)
                    mminlowerbound = convertStrToInt(os.environ.get(MIN_LOWER_BOUND + istr, str(_ML_MIN_LOWER_BOUND)),
                                                     _ML_MIN_LOWER_BOUND)
                    config.setThresholdKV(mtype, THRESHOLD, mthreshold)
                    config.setThresholdKV(mtype, BOUND, mbound)
                    config.setThresholdKV(mtype, MIN_LOWER_BOUND, mminlowerbound)
    
        _ML_PROPHET_PERIOD = convertStrToInt(os.environ.get(PROPHET_PERIOD, str(DEFAULT_PROPHET_PERIOD)),
                                            DEFAULT_PROPHET_PERIOD)
        _ML_PROPHET_FREQ = os.environ.get(PROPHET_FREQ, DEFAULT_PROPHET_FREQ)
        # prophet algm parameters end
    
        #ML_PAIRWISE_ALGORITHM = os.environ.get(PAIRWISE_ALGORITHM, ALL)
        #ML_PAIRWISE_THRESHOLD = convertStrToFloat(os.environ.get(PAIRWISE_THRESHOLD, str(DEFAULT_PAIRWISE_THRESHOLD)),
        #                                          DEFAULT_PAIRWISE_THRESHOLD)
    
        #MAX_STUCK_IN_SECONDS = convertStrToInt(os.environ.get('MAX_STUCK_IN_SECONDS', str(DEFAULT_MAX_STUCK_IN_SECONDS)),
        #                                       DEFAULT_MAX_STUCK_IN_SECONDS)
        _min_historical_data_points = convertStrToInt(
            os.environ.get('MIN_HISTORICAL_DATA_POINT_TO_MEASURE', str(DEFAULT_MIN_HISTORICAL_DATA_POINT_TO_MEASURE)),
            DEFAULT_MIN_HISTORICAL_DATA_POINT_TO_MEASURE)
        
    @property
    def min_historical_data_points(self):
        return self._min_historical_data_points
    
    @property
    def ML_PROPHET_FREQ(self):
        return self._ML_PROPHET_FREQ
    
    @property
    def ML_PROPHET_PERIOD(self):
        return self._ML_PROPHET_PERIOD
    
    @property
    def metric_threshold_count(self):
        return self._metric_threshold_count
    
    @property
    def ML_ALGORITHM(self):
        return self._ML_ALGORITHM
    
    @property
    def ML_LOWER_THRESHOLD(self):
        return self._ML_LOWER_THRESHOLD  
    
    @property
    def FOREMAST_SERVICE_URL(self):
        return self._FOREMAST_SERVICE_URL 
    
    @property
    def CURRENT_CONF_POD_TIME_WINDOW(self):
        return self._CURRENT_CONF_POD_TIME_WINDOW 
    
    @property
    def HISTORICAL_CONF_TIME_WINDOW(self):
        return self._HISTORICAL_CONF_TIME_WINDOW
    
    @property
    def CURRENT_CONF_TIME_WINDOW(self):
        return self._CURRENT_CONF_TIME_WINDOW 
    
    @property
    def ML_BOUND(self):
        return self._ML_BOUND
    
    @property
    def ML_MIN_LOWER_BOUND(self):
        return self._ML_MIN_LOWER_BOUND 

   

    
    
    