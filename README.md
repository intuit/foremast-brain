# Foremast

## Foremast-brain


### What It Does
Foremast-brain makes health judgment of a service health detection and canary analysis system for Kubernetes. There are two sets of evaluations Foremast-brain made :

1. Check if the baseline and current health metric has the same distribution pattern.
2. Calculate the historical model and detect current metric anomalies

Foremast-brain will make judgment health or unhealthy based on the evaluation result. 

Please check out the Check out the [architecture and design](https://github.com/intuit/foremast/blob/master/docs/design.md) for deatil

### Overwrite default algorithm, parameters 
There are multiple sets of parameters can be overwritten.

#### machine learning algorithm related parameters -- used for post-deployment use cases
 ML_ALGORITHM --- algorithm which you want to pick Please refer to  [AI_MODEL](https://github.com/intuit/foremast-brain/blob/master/src/models/modelclass.py) for all the supported algorithms
 
 MIN_HISTORICAL_DATA_POINT_TO_MEASURE -- minimum historical data points size
 
 ML_BOUND -- measurement is upper bound, lower bound or upper and lower bound
 
 ML_THRESHOLD --- threshold
 
#### performance, fault-tolerant related parameters
MAX_STUCK_IN_MINUTES ---- max process time until another foremast-brain process will take over and reprocess

MAX_CACHE_SIZE  --- max cached model size

#### pairwise algorithm parameters---used for pre-deployment use cases
 ML_PAIRWISE_ALGORITHM -- there are multiple options: ALL, ANY, MANN_WHITE, WILCOXON, KRUSKAL, etc.
 
 ML_PAIRWISE_THRESHOLD --  pairwise algorithm threshold
 
 MIN_MANN_WHITE_DATA_POINTS -- minimum data points required by Mann-Whitney U algorithm.

MIN_WILCOXON_DATA_POINTS -- minimum data points required by Wilcoxon algorithm.

MIN_KRUSKAL_DATA_POINTS -- minimum data points required by Kruskal algorithm.


### How to make change:
You can add algorithm name, different parameters Please refer [foremast-brain.yaml] (https://github.com/intuit/foremast/blob/master/deploy/foremast/3_judgement/foremast-brain.yaml) for detail

You can refer below ES_ENDPOINT as an example

```
env:
- name: ES_ENDPOINT
  value: "http://elasticsearch-discovery.foremast.svc.cluster.local:9200"
```





