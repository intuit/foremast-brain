from globalconfig import globalconfig

x =  globalconfig()
x.setKV('a',1)
x.setKV('b', 3) 
y = globalconfig()
y.setKV('dd',4)

print(y.getKVs())
