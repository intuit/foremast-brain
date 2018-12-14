
from urllib import request, error


def dorequest(url, data = '', method = 'GET'):
    try: 
        if method == 'GET':
            resp = request.urlopen(url, timeout=10).read()
        else:
            # use PUT/DELETE/POST, data should be encoded in ascii/bytes 
            req = request.Request(url, data = data.encode('ascii'), method = method)
            resp = request.urlopen(request, timeout=10).read()
    # etcd may return json result with response http error code
    # http error code will raise exception in urlopen
    # catch the HTTPError and get the json result
    except error.HTTPError as e:
        # e.fp must be read() in this except block.
        # the e will be deleted and e.fp will be closed after this block
        resp = e.fp.read()
    # response is encoded in bytes. 
    # recoded in utf-8 and loaded in json
    #return str(resp, encoding='utf-8')
    return resp.decode('utf-8')

        

