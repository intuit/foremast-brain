import json
import pandas as pd
from datetime import datetime as dt




CONFIG_SEPARATE =' ||'
KV_SEPARATE = '== ' 

def convertStrToJson(content):
    return json.loads(content)
    
def convertArrayListToDataFrame(arrayList):
    i = 0
    ts =[]
    vals = []
    while i <= len(arrayList)-1:
        ts.append(dt.utcfromtimestamp(int(arrayList[i][0])))
        vals.append(float(arrayList[i][1]))
        i +=1
    data_frame = addHeader(ts,vals) 
    return data_frame
  
  
# the purpose to convert dataframe with ds and y is to make fbprophet happy 
def addHeader(ts_idx, values, ts=[], isTSIndexOnly=True, tsname='ds', valname='y'):
    d = {valname:values}
    if isTSIndexOnly==False and len(ts) == len(ts_idx):
        d = { tsname:ts, valname:values}
    df = pd.DataFrame(data=d, index=ts_idx)
    #sort by ts by default 
    if isTSIndexOnly: 
        df=df.sort_index()
    return df



def convertStringToMap(mystr, sep1=CONFIG_SEPARATE, sep2=KV_SEPARATE):
    if mystr is None or mystr=='':
        return None
    list = mystr.split(sep1)
    #below code is backward compatible (will remove once sheldon upgraded
    mymap = dict()
    for x in list:
        li = x.split(sep2)
        if (len(li)>1):
            mymap[li[0]]=li[1]
    return mymap

def convertStrToInt(mystr, defaultInt):
    ret = defaultInt
    try:
        ret = int(mystr)
    except ValueError:
        ret= defaultInt
    return ret
    
def convertStrToFloat(mystr, defaultInt):
    ret = defaultInt
    try:
        ret = float(mystr)
    except ValueError:
        ret= defaultInt
    return ret
