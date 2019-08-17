from scipy.stats import mannwhitneyu, wilcoxon,kruskal,friedmanchisquare
from metadata.globalconfig import globalconfig
from mlalgms.statsmodel import IS_UPPER_BOUND,IS_UPPER_O_LOWER_BOUND,IS_LOWER_BOUND
import warnings                                  
warnings.filterwarnings('ignore')


########################################
#
#   This package could use for
#   canary deploy
#
########################################



MANN_WHITE = "mannwhitneyu"
WILCOXON = "wilcoxon"
KRUSKAL = "kruskal"
FRIED_MANCHI_SQUARE = "friedmanchisquare"
ALL = "all"
ANY = "any"
ERROR = "error"

MANN_WHITE_MIN_DATA_POINT =20
WILCOXON_MIN_DATA_POINTS =20
KRUSKAL_MIN_DATA_POINTS = 5

DEFAULT_PAIRWISE_THRESHOLD = 0.05


def TwoDataSetSameDistribution(dataset1, dataset2, alpha=DEFAULT_PAIRWISE_THRESHOLD, algorithm=ANY, bound= IS_UPPER_BOUND):
  config = globalconfig()
  
  size = min(len(dataset1),len(dataset2))
  p = 0
  if algorithm == WILCOXON:
      try:
          stat, p = wilcoxon(dataset1, dataset2,"pratt", True)
          if p >= alpha:
              return True, p, WILCOXON,size>=config.getValueByKey("MIN_WILCOXON_DATA_POINTS")
          else:
              return False, p, WILCOXON, size>=config.getValueByKey("MIN_WILCOXON_DATA_POINTS")
      except Exception as e:
          try:
              if (bound== IS_UPPER_BOUND):
                  stat, p = mannwhitneyu(dataset1, dataset2,True, 'greater')
              elif bound == IS_LOWER_BOUND :
                  stat, p = mannwhitneyu(dataset1, dataset2,True, 'less')
              else:
                  stat, p = mannwhitneyu(dataset1, dataset2,True, 'two-sided')
              if p >= alpha:
                  return True, p , MANN_WHITE, size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS")
              else:
                  return False, p,  MANN_WHITE, size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS") 
          except Exception as e:
                  return True, 0, ERROR , size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS") 
  elif algorithm == KRUSKAL:
      try:
          stat, p = kruskal(dataset1, dataset2)
          if p >= alpha:
              return True, p,KRUSKAL, size>=config.getValueByKey("MIN_KRUSKAL_DATA_POINTS")
          else:
              return False, p,KRUSKAL, size>=config.getValueByKey("MIN_KRUSKAL_DATA_POINTS")
      except Exception as e:
          try:
              if (bound== IS_UPPER_BOUND):
                  stat, p = mannwhitneyu(dataset1, dataset2,True, 'greater')
              elif bound == IS_LOWER_BOUND :
                  stat, p = mannwhitneyu(dataset1, dataset2,True, 'less')
              else:
                  stat, p = mannwhitneyu(dataset1, dataset2,True, 'two-sided')
              if p >= alpha:
                  return True, p , MANN_WHITE, size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS")
              else:
                  return False, p,  MANN_WHITE, size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS")
          except Exception as e:
                  return True, 0, ERROR, size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS") 
  elif algorithm == ALL:
      try:
          if (bound== IS_UPPER_BOUND):
            stat, p = mannwhitneyu(dataset1, dataset2,True, 'greater')
          elif bound == IS_LOWER_BOUND :
            stat, p = mannwhitneyu(dataset1, dataset2,True, 'less')
          else:
            stat, p = mannwhitneyu(dataset1, dataset2,True, 'two-sided')
          if p >= alpha:
              stat, p = wilcoxon(dataset1, dataset2,"pratt", True)
              if p >= alpha:
                  stat, p = kruskal(dataset1, dataset2)
                  if p >= alpha:
                      return True, p, ALL, size>=config.getValueByKey("MIN_KRUSKAL_DATA_POINTS")
                  else:
                      return False, p, KRUSKAL, size>=config.getValueByKey("MIN_KRUSKAL_DATA_POINTS")
              else:
                  return False, p, WILCOXON, size>=config.getValueByKey("MIN_WILCOXON_DATA_POINTS")
          else:
              return False, p, MANN_WHITE, size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS")

      except Exception as e:
          try:
              if (bound== IS_UPPER_BOUND):
                  stat, p = mannwhitneyu(dataset1, dataset2,True, 'greater')
              elif bound == IS_LOWER_BOUND :
                  stat, p = mannwhitneyu(dataset1, dataset2,True, 'less')
              else:
                  stat, p = mannwhitneyu(dataset1, dataset2,True, 'two-sided')
              if p >= alpha:
                  return True, p , MANN_WHITE, size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS")  
              else:
                  return False, p,  MANN_WHITE, size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS") 
          except Exception as e:
                  return True, 0, ERROR ,  MANN_WHITE, size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS") 
  elif algorithm == ANY:
      try:
          if (bound== IS_UPPER_BOUND):
              stat, p = mannwhitneyu(dataset1, dataset2,True, 'greater')
          elif bound == IS_LOWER_BOUND :
              stat, p = mannwhitneyu(dataset1, dataset2,True, 'less')
          else:
              stat, p = mannwhitneyu(dataset1, dataset2,True, 'two-sided')
          if p >= alpha:
              return True, p, MANN_WHITE, size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS")
          stat, p = wilcoxon(dataset1, dataset2,"pratt", True)
          if p >= alpha:
              return True, p, WILCOXON, size>=config.getValueByKey("MIN_WILCOXON_DATA_POINTS")
          stat, p = kruskal(dataset1, dataset2)
          if p >= alpha:
                return True, p, KRUSKAL, size>=config.getValueByKey("MIN_KRUSKAL_DATA_POINTS")
          return False, p, ANY, size>=config.getValueByKey("MIN_KRUSKAL_DATA_POINTS")
      except Exception as e:
          try:
              if (bound== IS_UPPER_BOUND):
                  stat, p = mannwhitneyu(dataset1, dataset2,True, 'greater')
              elif bound == IS_LOWER_BOUND :
                  stat, p = mannwhitneyu(dataset1, dataset2,True, 'less')
              else:
                  stat, p = mannwhitneyu(dataset1, dataset2,True, 'two-sided')
              if p >= alpha:
                  return True, p , MANN_WHITE, size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS") 
              else:
                  return False, p,  MANN_WHITE, size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS") 
          except Exception as e:
                  return True, 0, ERROR , size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS")  
  else:
      try:
          if (bound== IS_UPPER_BOUND):
              stat, p = mannwhitneyu(dataset1, dataset2,True, 'greater')
          elif bound == IS_LOWER_BOUND :
              stat, p = mannwhitneyu(dataset1, dataset2,True, 'less')
          else:
              stat, p = mannwhitneyu(dataset1, dataset2,True, 'two-sided')
          if p >= alpha:
              return True, p , MANN_WHITE, size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS")  
          else:
              return False, p,  MANN_WHITE, size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS") 
      except Exception as e:
          if str(e) ==  "All numbers are identical in mannwhitneyu" :
              return True, 0, MANN_WHITE, size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS")                 
  return True,  0, ERROR,  size>=config.getValueByKey("MIN_MANN_WHITE_DATA_POINTS")
  
  
  
def MultipleDataSetSameDistribution(list,  alpha = DEFAULT_PAIRWISE_THRESHOLD, algorithm=KRUSKAL): 
    stat=0
    p=0
    length = len(list)
    size = 0
    if algorithm == KRUSKAL:
        if length==3:
            size = min(len(list[0]), len(list[1]), len(list[2]))
            stat, p = kruskal(list[0], list[1], list[2])
        elif length==4:
            size = min(len(list[0]), len(list[1]), len(list[2]), len(list[3]))
            stat, p = kruskal(list[0], list[1], list[2],list[3])
        elif length==5:
            size = min(len(list[0]), len(list[1]), len(list[2]), len(list[3]), len(list[4]))
            stat, p = kruskal(list[0], list[1], list[2],list[3],list[4])
        elif length==6:
            size = min(len(list[0]), len(list[1]), len(list[2]), len(list[3]), len(list[4]),len(list[5]))
            stat, p = kruskal(list[0], list[1], list[2],list[3],list[4],list[5])        
        else:
            size = minSize(list)
            stat, p = kruskal(*list)
        if p >= alpha:
            return True, p, KRUSKAL, size>=config.getValueByKey("MIN_KRUSKAL_DATA_POINTS")
        else:
            return False, p, KRUSKAL, size>=config.getValueByKey("MIN_KRUSKAL_DATA_POINTS")
    elif algorithm == FRIED_MANCHI_SQUARE:
        if length==3:
            stat, p =friedmanchisquare(list[0], list[1], list[2])
        elif length==4:
            stat, p = friedmanchisquare(list[0], list[1], list[2],list[3])
        elif length==5:
            stat, p = friedmanchisquare(list[0], list[1], list[2],list[3],list[4])
        elif length==6:
            stat, p = friedmanchisquare(list[0], list[1], list[2],list[3],list[4],list[5])            
        else:
            stat, p = friedmanchisquare(*list)
        if p >= alpha:
            return True, p,FRIED_MANCHI_SQUARE,True
        else:
            return False,p,FRIED_MANCHI_SQUARE,True 
    return Ture,p, ERROR,True

def minSize(list):
    min = 0
    for data in list:
        if min > len(data):
            min = len(data)
    return min
        
        
     

'''
 
def MultipleDataSetSameDistribution(*dataset,algorithm=KRUSKAL, alpha = DEFAULT_PAIRWISE_THRESHOLD):
    if algorithm == FRIED_MANCHI_SQUARE:
          stat, p = friedmanchisquare(*dataset)
          if p >= alpha:
              return True,p
          else:
              return False,p
    else:
          stat, p = kruskal(*dataset)
          if p >= alpha:
              return True,p
          else:
              return False,p
    return False,p   
    ''' 