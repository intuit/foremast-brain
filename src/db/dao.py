from abc import abstractmethod


class PersistStore(object):
    def __init__(self, configUrl):
        self.url = configUrl
    @abstractmethod    
    def store(self, key, value):pass
    @abstractmethod 
    def get(self, key):pass
    @abstractmethod 
    def remove(self, key):pass
    

    

class MetaData(PersistStore):
    def __init__(self,key,value):
        super().__init__(key,value)
        self.prefix = "md_"