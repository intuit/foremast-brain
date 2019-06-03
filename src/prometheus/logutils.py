import time
import logging

logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('logutils')


def logit(method):
    """
    A decorator that logs call and the time a function takes
    :param method:
    :return:
    """
    def timed(*args, **kw):
        ts = time.time()
        logger.warning("Method %s called", method.__name__)
        result = method(*args, **kw)
        te = time.time()
        logger.warning("Method %s took %2.2f ms", method.__name__, (te - ts) * 1000)
        return result
    return timed