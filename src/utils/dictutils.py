

def retrieveKVList(dicts):
    keys=[]
    values=[]
    for key ,value in dicts.items():
        keys.append(key)
        values.append(value)
    return keys, values


    
def convertDictKey(mydict,replacefrom, replaceto):
    for key in mydict:
        mydict[key.replace(replacefrom,replaceto)] = mydict.pop(key)
    return mydict
