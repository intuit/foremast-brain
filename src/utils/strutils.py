


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







