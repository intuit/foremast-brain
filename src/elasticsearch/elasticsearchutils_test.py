import os

from elasticsearchutils import searchByStatus, buildElasticSearchUrl


ES_ENDPOINT = os.environ.get('ES_ENDPOINT', 'http://aa41f5f30e2f011e8bde30674acac93e-1024276836.us-west-2.elb.amazonaws.com:9200')    
ES_INDEX = 'documents'   
es_url_status_search=buildElasticSearchUrl(ES_ENDPOINT, ES_INDEX)
es_url_status_update=buildElasticSearchUrl(ES_ENDPOINT, ES_INDEX, isSearch=False)
tt= searchByStatus(es_url_status_update, "initial", True, 10)