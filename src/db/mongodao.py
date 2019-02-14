from pymongo import MongoClient
from datetime import datetime
import json

class mongoStore:
    def __init__(self,url):
        self.url = url
        client = MongoClient(url)
        db = client.admin
        self.collection = db.appConfig
    def insert(self,  key, appConfig, isModel=False):
        if isModel:
            key = key+'_model'
        result = self.collection.find_one({ '_id':key})
        if result==None:
            result= self.collection.insert_one(appConfig)
        return result    
    
    
    def update(self, key, updatedMap, isModel=False): 
        if isModel:
            key = key+'_model'
        result = self.collection.find_one({ '_id':key})
        if (result==None):   
            return result
        result = self.collection.update_one({'_id':key},
            {'$set': updatedMap,              
             '$currentDate':{'last_modified_date':True}               
        })
        return result

    def delete(self, key, isModel=False): 
        if isModel:
            key = key+'_model'    
        ret = self.collection.delete_many({ '_id':key})
        return ret
    
    def find(self, key, isModel=False):
        if isModel:
            key = key+'_model' 
        appConfig = self.collection.find_one({ '_id':key})
        return appConfig
    def findAll(self, filter=None):
        if filter == None:
            return self.collection.find()
        return self.collection.find(filter)