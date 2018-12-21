def retrieveKVList(dicts):
    keys=[]
    values=[]
    for key ,value in dicts.items():
        keys.append(key)
        values.append(value)
    return keys, values
