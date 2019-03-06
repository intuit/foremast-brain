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