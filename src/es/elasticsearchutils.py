import logging
import os
from string import Template
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from datetime import datetime, timezone

logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

INDEX_TYPE = "document"
REQ_INDEX_NAME = "documents"
LOG_INDEX_NAME = "hpalogs"
LOG_DOC_COUNT = 10
MODEL_DATA_INDEX_NAME = "model_datas"
MODEL_CONFIG_INDEX_NAME = "model_configs"
MODEL_PARAMETER_INDEX_NAME = "model_parameters"

# query by job id
payload_query_by_job_id = Template('''
{
    "query": {
        "bool": {
            "must": [{
                "match": {
                    "job_id": "$jobid"
                }
            }],
            "filter": [{
                "range": {
                    "modified_at": {
                        "gte": "now-${pass_sec}s/s"
                    }
                }
            }]
        }
    },
    "sort": [{
        "modified_at": {
            "order": "$order",
            "unmapped_type": "string"
        }
    }]
}
'''
)


# query by status list
payload_search_status_list2 = Template('''{
    "query": {
        "terms": {
            "status": ["$status"]
        }
    },
    "sort": [
        {
            "modified_at": {
                "order": "asc"
            }
        }
    ]
}''')

# query template by status and last modified
payload_search_status_with_filter = Template('''{
    "query": {
        "bool": {
            "must": [{
                "match": {
                    "status": "$status"
                }
            }],
            "filter": [{
                "range": {
                    "modified_at": {
                        "lt": "now-${pass_sec}s/s"
                    }
                }
            }]
        }
    },
    "sort": [{
        "modified_at": {
            "order": "asc"
        }
    }]
}''')


class ESClient:
    def __init__(self):
        """Initial to create necessary indexes, ignore if exist"""
        self.es = Elasticsearch(os.environ.get('ES_ENDPOINT', 'http://localhost:9200'))
        if not self.es.indices.exists(REQ_INDEX_NAME):
            self.es.indices.create(index=REQ_INDEX_NAME, ignore=400)
        if not self.es.indices.exists(LOG_INDEX_NAME):
            self.es.indices.create(index=LOG_INDEX_NAME, ignore=400)
        if not self.es.indices.exists(MODEL_DATA_INDEX_NAME):
            self.es.indices.create(index=MODEL_DATA_INDEX_NAME, ignore=400)
        if not self.es.indices.exists(MODEL_PARAMETER_INDEX_NAME):
            self.es.indices.create(index=MODEL_PARAMETER_INDEX_NAME, ignore=400)
        if not self.es.indices.exists(MODEL_CONFIG_INDEX_NAME):
            self.es.indices.create(index=MODEL_CONFIG_INDEX_NAME, ignore=400)

    def search_by_id(self, id, index_name=REQ_INDEX_NAME, doc_type=INDEX_TYPE):
        """
        Search request document by uuid
        :param id: request uuid from foremat-service
        :param index_name: default is documents
        :param doc_type: default is document
        :return: request doc
        """
        try:
            return self.es.get(index_name, doc_type=doc_type, id=id)
        except NotFoundError as ex:
            logger.debug('Document {} not found'.format(id))
            return None
        except Exception as e:
            logger.exception('Exception when calling elasticsearch API %s\n', e)
            return None

    def update_doc_status(self, uuid, status, info='', reason='', index_name=REQ_INDEX_NAME, doc_type=INDEX_TYPE):
        """
        Update request doc status
        :param uuid: identify the request
        :param status: COMPLETED_HEALTH
                       COMPLETED_UNHEALTH
                       COMPLETED_UNKNOWN
                       PREPROCESS_INPROGRESS
                       PREPROCESS_COMPLETED
                       PREPROCESS_FAILED
                       POSTPROCESS
                       INITIAL
                       ABORT
        :param info: additional information for status change
        :param reason: information why status got changed
        :param index_name: default is documents
        :param doc_type: default is document
        :return: True if doc updated
        """
        try:
            body = {'status': status}
            if info != '':
                body['info'] = info
            if reason != '':
                body['reason'] = reason
            body['modified_at'] = self.__get_now()

            bodies = {"doc": body}
            self.es.update(index_name, doc_type, uuid, body=bodies)
            return True
        except Exception as e:
            logger.exception('Exception when update doc %s with %s status %s\n', uuid, status, e)
            return False

    def search_status_and_lastmodify(self, status, pass_sec=3, index_name=REQ_INDEX_NAME, doc_type=INDEX_TYPE):
        """
        Seach doc by specified status and last modified time
        :param status: refer updateDocStatus
        :param pass_sec: compare last modified time with past second
        :param index_name: default is documents
        :param doc_type: default is document
        :return:
        """
        try:
            qry = payload_search_status_with_filter.substitute(status=status, pass_sec=pass_sec)
            return self.es.search(index_name, doc_type, body=qry)
        except Exception as e:
            logger.exception('Exception when search doc by status %s %s\n', status, e)
            return None

    def search_by_statuslist(self, *status, index_name=REQ_INDEX_NAME, doc_type=INDEX_TYPE):
        """
        Search request by list of status
        :param status: refer updateDocStatus
        :param index_name: default is documents
        :param doc_type: default is document
        :return:
        """
        try:
            sts = '","'.join(s for s in status)
            qry = payload_search_status_list2.substitute(status=sts)
            return self.es.search(index_name, doc_type, body=qry)
        except Exception as e:
            logger.exception('Exception when search doc by status %s\n', e)
            return None

    def save_reason(self, jobid, log_time, log_content, index_name=LOG_INDEX_NAME, doc_type=INDEX_TYPE):
        """
        Store HPA score change logs, the foremast-service will retrieve logs for audit
        :param jobid: application name : namespace : strategy
        :param log_time: log store time
        :param log_content: log entities
        :return:
        """
        try:
            body = {'job_id': jobid, 'hpalog': log_content, 'timestamp': log_time}
            res = self.es.search(index_name, doc_type,
                                 body=payload_query_by_job_id.substitute(jobid=jobid, order='asc', pass_sec=0))
            cnt, _ = self.parse_result(res)
            if cnt >= LOG_DOC_COUNT:
                # update the oldest doc
                body['modified_at'] = self.__get_now()
                self.es.update(index_name, doc_type, res['hits']['hits'][0]['_id'], body={"doc": body}, refresh=True)
            else:
                # create new log
                body['created_at'] = self.__get_now()
                body['modified_at'] = self.__get_now()
                self.es.index(index_name, doc_type, body=body, refresh=True)
            return True
        except Exception as e:
            logger.exception('Exception when save hpa logs {}'.format(jobid))
            return False

    def save_model(self, jobid, model_parameters={}, model_data={}, model_config={}):
        """
        Store model that can share with other components
        The parameters, data and config will be stored to different indexes, call API with named arguments is preferred
        :param jobid: application name:namespace:strategy for HPA, uuid for other strategy
        :param model_parameters:
        :param model_data:
        :param model_config:
        :return:
        """
        try:
            # construct model body for es
            body = {'job_id': jobid}
            if model_parameters:
                model_parameters['modified_at'] = self.__get_now()
                body['model_parameters'] = model_parameters
                self.__save_data(body, jobid, MODEL_PARAMETER_INDEX_NAME)
                    
            if model_data:
                model_data['modified_at'] = self.__get_now()
                body['model_data'] = model_data
                self.__save_data(body, jobid, MODEL_DATA_INDEX_NAME)
            if model_config:
                model_config['modified_at'] = self.__get_now()
                body['model_config'] = model_config
                self.__save_data(body, jobid, MODEL_CONFIG_INDEX_NAME)
            return True
        except Exception as e:
            logger.exception('Exception when save model {}'.format(jobid))
            return False
    
    def __save_data(self, body, jobid, index_name=None, doc_type=INDEX_TYPE):
        res = self.es.search(index_name, doc_type,
                                 body=payload_query_by_job_id.substitute(jobid=jobid, order='desc', pass_sec=0))
        cnt, _ = self.parse_result(res)
        if cnt > 0:
            # update the doc
            body['modified_at'] = self.__get_now()
            self.es.update(index_name, doc_type, res['hits']['hits'][0]['_id'], refresh=True, body={"doc": body})
        else:
            # create new doc
            body['created_at'] = self.__get_now()
            body['modified_at'] = self.__get_now()
            self.es.index(index_name, doc_type, refresh=True, body=body)
        

    def get_model_config(self, jobid, interval=864000000, index_name=MODEL_CONFIG_INDEX_NAME, doc_type=INDEX_TYPE):
        """
        Retrieve model config
        :param jobid: application name:namespace:strategy for HPA, uuid for other strategy
        :param interval config valid time
        :return:
        """
        return self.__get_data(jobid, 'model_config', interval, index_name, doc_type)

    def get_model_data(self, jobid, interval=1800, index_name=MODEL_DATA_INDEX_NAME, doc_type=INDEX_TYPE):
        """
        Retrieve model data
        :param jobid: application name : namespace : strategy
        :param interval data valid time
        :return:
        """
        return self.__get_data(jobid, 'model_data', interval, index_name, doc_type)

    def get_model_parameters(self, jobid, interval=1800, index_name=MODEL_PARAMETER_INDEX_NAME, doc_type=INDEX_TYPE):
        """
        Retrieve model parameters
        :param jobid: application name:namespace:strategy for HPA, uuid for other strategy
        :param interval parameters valid time
        :return:
        """
        return self.__get_data(jobid, 'model_parameters', interval, index_name, doc_type)

    def parse_result(self, res):
        """
        Parsing ES response
        :param res:
        :return: total document number and docs
        """
        list = []
        if 'hits' in res:
            count = res['hits']['total']
            hits = res['hits']['hits']
            if count > 0:
                for data in hits:
                    list.append(data['_source'])
        else:
            list.append(res['_source'])
        return len(list), list

    def __get_data(self, jobid, key, interval, index_name, doc_type=INDEX_TYPE):
        """
        Used by model retrieve methods
        :param jobid:
        :param key:
        :return:
        """
        try:
            res = self.es.search(index_name, doc_type,
                                 body=payload_query_by_job_id.substitute(jobid=jobid, order='desc', pass_sec=interval))
            cnt, list = self.parse_result(res)
            if cnt > 0 and key in list[0]:
                return list[0][key]
            return None
        except Exception as e:
            logger.exception('Exception when get {} for {}'.format(key, jobid))
            return None

    def __get_now(self):
        """
        Get current time
        :return:
        """
        local_time = datetime.now(timezone.utc).astimezone()
        return local_time.isoformat()