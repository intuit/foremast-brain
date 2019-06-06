from es.elasticsearchutils import ESClient
from es.elasticsearchutils import payload_query_by_job_id

from datetime import timezone, datetime, timedelta
import time

import unittest


class TestESUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.es = ESClient()
        cls.es.es.index("test_index", "doc", id="id001",
                    body={"field": "value", "status": "initial",
                          "modified_at": datetime.now(timezone.utc).astimezone()})
        cls.es.es.index("test_index", "doc", id="id002", body={"status": "in_test", "modified_at": (
                datetime.now(timezone.utc) - timedelta(days=1)).astimezone()})
        cls.es.es.indices.create("hpalogs_test", ignore=400)
        cls.es.es.indices.refresh('test_index', ignore=400)
        cls.es.es.indices.refresh('hpalogs_test', ignore=400)

    @classmethod
    def tearDownClass(cls):
        cls.es.es.indices.delete("test_index")
        cls.es.es.indices.delete("hpalogs_test")
        print("how many")
        cls.es.es.delete_by_query('_all',
                                  payload_query_by_job_id.substitute(jobid='application:namespace:stragegy', order='asc'))

    def test_search_by_id(self):
        resp = self.es.search_by_id("dummy_id")
        assert resp is None
        resp = self.es.search_by_id("id001", "test_index", "doc")
        assert resp is not None
        resp = self.es.search_by_id("exception", "exception")
        assert resp is None

    def test_update_doc_status(self):
        self.es.update_doc_status("id001", "new_status", "new info", "new reason", index_name="test_index",
                                      doc_type="doc")
        resp = self.es.search_by_id("id001", "test_index", "doc")
        assert resp is not None
        cnt, doc = self.es.parse_result(resp)
        assert cnt == 1
        assert doc[0]['status'] == "new_status"

    def test_search_status_and_lastmodify(self):
        resp = self.es.search_status_and_lastmodify("in_test", pass_sec=3, index_name="test_index", doc_type="doc")
        cnt, list = self.es.parse_result(resp)
        assert cnt == 1
        resp = self.es.search_status_and_lastmodify("in_test", pass_sec=2 * 24 * 60 * 60, index_name="test_index",
                                                        doc_type="doc")
        cnt, list = self.es.parse_result(resp)
        assert cnt == 0

    def test_search_by_statuslist(self):
        resp = self.es.search_by_statuslist("in_test", index_name="test_index", doc_type="doc")
        cnt, list = self.es.parse_result(resp)
        assert cnt == 1

    def test_save_reason(self):
        qry = {
            "query": {
                "terms": {
                    "job_id": ["log_id"]
                }
            },
            "sort": [{
                "modified_at": {
                    "order": "asc",
                    "unmapped_type": "string"
                }
            }]
        }

        for i in range(11):
            self.es.save_reason('log_id', datetime.now(timezone.utc).astimezone(),
                                    {"content": "change logs" + str(i)},
                                    index_name='hpalogs_test')
        res = self.es.es.search('hpalogs_test', 'document', body=qry)
        assert res['hits']['total'] == 10
        for i in range(2):
            self.es.save_reason('log_id', datetime.now(timezone.utc).astimezone(),
                                    {"content": "change logs" + str(20 + i)}, index_name='hpalogs_test')
        res = self.es.es.search('hpalogs_test', 'document', body=qry)
        cnt, list = self.es.parse_result(res)
        assert cnt == 10
        expect_list = ['change logs3', 'change logs4', 'change logs5', 'change logs6', 'change logs7', 'change logs8',
                       'change logs9', 'change logs10', 'change logs20', 'change logs21']
        got_list = []
        for i in range(10):
            got_list.append(list[i]['hpalog']['content'])
        assert got_list == expect_list

    def test_save_model(self):
        qry = {
            "query": {
                "match": {"job_id": "application:namespace:stragegy"}
            },
            "sort": [{
                "modified_at": {
                    "order": "desc",
                    "unmapped_type": "string"
                }
            }]
        }

        self.es.save_model('application:namespace:stragegy', model_parameters={"parameter1": "val1"})
        res = self.es.es.search('model_parameters', 'document', body=qry)
        assert res is not None
        for i in range(10):
            self.es.save_model('application:namespace:stragegy', model_parameters={"parameter1": "val1" + str(i)})
        res = self.es.es.search('model_parameters', 'document', body=qry)
        cnt, list = self.es.parse_result(res)
        assert cnt == 1
        assert list[0]['model_parameters']['parameter1'] == "val19"

        self.es.save_model('application:namespace:stragegy', model_data={"data": "val1"})
        res = self.es.es.search('model_datas', 'document', body=qry)
        cnt, _ = self.es.parse_result(res)
        assert cnt == 1
        self.es.save_model('application:namespace:stragegy', model_config={"config": "config1"})
        res = self.es.es.search('model_configs', 'document', body=qry)
        cnt, _ = self.es.parse_result(res)
        assert cnt == 1

    def test_get_model(self):
        self.es.save_model('application:namespace:stragegy', model_parameters={"parameter": "param01"})
        param = self.es.get_model_parameters('application:namespace:stragegy')
        assert param['parameter'] == 'param01'

        self.es.save_model('application:namespace:stragegy', model_data={"data": "data01"})
        data = self.es.get_model_data('application:namespace:stragegy')
        assert data['data'] == 'data01'

        self.es.save_model('application:namespace:stragegy', model_config={"config": "conf01"})
        time.sleep(2)
        conf = self.es.get_model_config('application:namespace:stragegy', 0)
        assert conf is None

if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()
