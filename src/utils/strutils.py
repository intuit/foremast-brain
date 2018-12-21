def strcat(*strs):
    "Concats the given list of strings."
    return ''.join(strs)

def listToString(list, sep=' '):
    "Joins the given list of items by the given separator."
    return sep.join(list)

def escapeQuotes(query):
    bad_chars = [ ('"', "&quot;" ),("'", "&quot;")]
    for char, replacement in bad_chars:
        query = query.replace(char, replacement)

    return query
