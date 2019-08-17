import etcd
import os
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

#python3.5 -m pip install python-etcd





def getCon():
    config = ConfigParser()
    config.read("/Users/pzou/eclipse-workspace/python/aiengine/config/db.ini")
    dbserver = config.get('etcd_db','server')
    print(dbserver)
    dbport = config.get('etcd_db','port')
    print(dbport)


def getEtcdClient():
  return getEtcdClient(dbserver, dbport)


def getEtcdClient(port):
   return etcd.Client(port=port);

 
	
def getEtcdClient(host, port):
	return etcd.Client(host=host,port=port)
	
	
def getEtcdClient(host, port):
	return etcd.Client(host=host,port=port)
	
#def getEtcdClient(host1, host2, host3, port1, port2, port3):
#	return etcd.Client(host=((host1, port1), (host2, port2),(host3, port3)))
	

def write(client, key, value, ttlInSec=-1):
	if ttlInSec==-1:
		client.write(key, value)
	else:
		client.write(key, value, ttl=ttlInSec)

def update(client, key, value):
   	client.set(key, value)
   	
def read(client, key):
	try:
		return client.read(key).value
	except etcd.EtcdKeyNotFound:
		return None
	
def delete(client, key):
	client.delete(key)
	
def append(client, key, value):
	client.write(key, value, append=True)
	
def list(client, key):
	list = []
	directory = client.get(key)
	for result in directory.children:
  		print(result.key + ": " + result.value)	
  		
 
 	
if __name__ == '__main__':

        print(getEtcdClient()) 			
	
	
	
	