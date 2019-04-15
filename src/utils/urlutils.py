import urllib3




def dorequest(url, data = '', method = 'GET'):
  http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=10.0, read=10.0))
  try:
    if method == 'GET':
        resp = http.request(
           'GET',
          url)
        return resp.data.decode('utf-8')
    else: 
        resp = http.request(
        'POST',
        url,
        fields=data.encode('ascii')) 
        return resp.data.decode('utf-8')  
  except Exception as e:
    print("dorequest error",url,"  error ",str(e))
  return '' 
  


'''
from urllib import request, error
def dorequest(url, data = '', method = 'GET'):
    try: 
        if method == 'GET':
            resp = request.urlopen(url, timeout=10).read()
        else:

            req = request.Request(url, data = data.encode('ascii'), method = method)
            resp = request.urlopen(request, timeout=10).read()
    except error.HTTPError as e:
        resp = e.fp.read()
    return resp.decode('utf-8')
'''
        

