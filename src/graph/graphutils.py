import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
from IPython.core.pylabtools import figsize

def showGraph(name,df):
    ll = df.index.tolist()
    plt_ds = [date2num(dd)  for dd in ll]
    plt.figure(figsize=(15, 7))
    plt.plot_date(plt_ds, df.y)
    plt.title(name+' timeseries')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Metric Value')
    plt.show()
    
    
    
def showComparsionGraph(df):    
    df.plot(x='timestamp', y=['prediction', 'actual'], style=['r', 'b'], figsize=(15, 8))
    plt.xlabel('timestamp', fontsize=12)
    plt.ylabel('y', fontsize=12)
    plt.show()