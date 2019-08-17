class PersistData:
	def __init__(self,key,value):
		self.prefix = None
		self.key = key
		self.value = value

	def getKey(self):
		return self.prefix+self.key
	def setKey(key):
		self.key=key		
	def getValue(self):
		return self.value
	def setValue(value):
		self.value = value
	

class MetaData(PersistData):
	def __init__(self,key,value):
		super().__init__(key,value)
		self.prefix = "md_"

       
       
class DataModel (PersistData):
	def __init__(self,key,value):
		super().__init__(key,value)
		self.prefix = "dm_" 
  
       
       
 
class DataFactory(object):
 	@staticmethod
 	def createData(type, key, value):
 		if type=='MetaData': 
 			return MetaData(key,value)
 		elif type == 'DataModel':
 			return DataModel(key,value)
 			 
     
   	
      
	
if __name__ == '__main__':

        print(DataFactory.createData("MetaData", "key","value").getKey())
          