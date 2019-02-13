from mongodao import mongoStore


mongourl = 'mongodb://foremast:brain@localhost:27017/'
mongo = mongoStore(mongourl)

appConfig = {
    '_id':'appname',
    'status':'active',
    'model':'modelname',
    'model_parameters':{
        'zscore':'3'
    },
    'last_modified_date':'',
    
    'error5xx':
    {
        'source':'prometheus',
        'weight_pct':'70',
        'zscore':'2'
    },
    'error4xx':
    {
        'source':'prometheus',
        'weight_pct':'10',
        'zscore':'3'
    },
    'latency':
    {
        'source':'prometheus',
        'weight_pct':'10',
        'zscore':'4'
    }, 
    'cpu':
    {
        'source':'prometheus',
        'weight_pct':'5',
        'zscore':'5'
    },
    'memory':
    {
        'source':'prometheus',
        'weight_pct':'5',
        'zscore':'5'
    }
}



result = mongo.insert("appname",appConfig)

print(result)

map = {'model_parameters.zscore':1.97,'error5xx.zscore':1.97}
print(type(map))
      
ret = mongo.update("appname", map)
print(ret)

ret = mongo.find("appname")
print(ret)

cursor = mongo.findAll(None)
for record in cursor: 
    print(record)
    
    
mongo.delete("appname")

ret = mongo.find("appname")
print(ret)
