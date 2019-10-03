

def strcat(str0,str1,str2=''):
    output = []
    output.append(str0)
    output.append(str1)
    if str2!='':
       output.append(str2) 
    return ''.join(output)  

def listToString(list, sep=' '):
    return ''.join(str(s)+sep for s in list) 


def queryEscape(query):
    bad_chars = [ ('"', "&quot;" ),("'", "&quot;")]
    for char, replacement in bad_chars:
        query = query.replace(char, replacement)
 
    return query


def escapeString(list):
    if list=='':
        return list
    output = queryEscape(list)
    return output

def findSubStr(origstr, startstr, endstr):
    if (origstr is None or origstr == ''):
        return origstr
    pos1 = origstr.find(startstr)
    pos2 = origstr.find(endstr)
    if pos1==-1 or pos2==-1 :
       return None
    pos1 += len(startstr)
    if (pos1>=pos2):
        return None
    newUrl = origstr[pos1:pos2]
    return newUrl


def strReplace(origstr, startstr, endstr, replacestr):
    if (origstr is None or origstr == ''):
        return origstr
    pos1 = origstr.find(startstr)
    pos2 = origstr.find(endstr)
    if pos1==-1 or pos2==-1 :
       return origstr
    if (pos1>=pos2):
        return origstr
    
    newurl = origstr[:pos1]+startstr+str(replacestr)+origstr[pos2:]
    return newurl





