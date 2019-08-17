import pandas


def mergeDF(left, right):   
    return pandas.merge(left, right,how='outer', on='ds') 
        
        
        
def mergeColumnmap(leftColumnmap, rightColumnmap, mergedColumnlist):  
    columnmap={}
    count =1
    for key, value in leftColumnmap.items():
        if key == 'ds':
            continue
        columnmap[mergedColumnlist[count]]= value
        count +=1     
    for key, value in rightColumnmap.items():
        if key == 'ds':
            continue
        columnmap[mergedColumnlist[count]]= value
        count +=1  
    return columnmap



# dataframe summary. Can be used on notebook
def dataSummary(df):
    for column in df.columns:
        print(column)
        if df.dtypes[column] == np.object: # Categorical data
            print(df[column].value_counts())
        else:
            print(df[column].describe())
        print('\n')



