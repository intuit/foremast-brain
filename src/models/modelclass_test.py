from models.modelclass import ModelHolder   
modelHolder = ModelHolder('testMetric',{'threshold':5,'model':'model1'}, {'mean':5,'std':8})
print(modelHolder)


car =    {
  "brand": "Ford",
  "model": "Mustang",
  "year": 1964
}
car["cde"] ="efg"
aaa = car.get("abc")

if (aaa==None):
    print(car)