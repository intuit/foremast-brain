# Foremast

## Foremast-brain


### What It Does
Foremast-brain makes health judgement of a service health detection and canary analysis system for Kubernetes.
There are two set of evaluations Foremast-brain mades :

1. Check if baseline and current health metric has same distribution pattern.
2. Calculate the historical model and detect current metric anomalies 

Foremast-brain will made judgement health or unhealth based on evaluation result.
Please check out the Check out the [architecture and design](https://github.com/intuit/foremast/blob/master/docs/design.md) for deatil

### Overwrite default algorithm, parameters 
There are multiple set of parameters can be overwritten.

#### machine learning algorithm related parameters -- used for post deployment use cases
 ML_ALGORITHM --- algorithm which you want to pick  Please refer to AI_MODEL for all the supported algorithms
 
 MIN_HISTORICAL_DATA_POINT_TO_MEASURE -- minimum historical data points size
 
 ML_BOUND -- measurement is upper bound , lower bound or upper and lower bound
 
 ML_THRESHOLD --- threshould
 
#### performance, fault tolerant related parameters
MAX_STUCK_IN_MINUTES ---- max process time until another foremast-brain process will take over and reprocess

MAX_CACHE_SIZE  --- max cached model size 

#### pairwise algorithm parameters---used for pre-deployment use cases
 ML_PAIRWISE_ALGORITHM -- there are multiple options: ALL, ANY, MANN_WHITE,WILCOXON, KRUSKAL, etc.
 
 ML_PAIRWISE_THRESHOLD -- pairwise algorithm threshold
 
 MIN_MANN_WHITE_DATA_POINTS -- minimum data points required by mannwhitneyu algorithm.
 
 MIN_WILCOXON_DATA_POINTS -- minimum data points required by wilcoxon algorithm.
 
 MIN_KRUSKAL_DATA_POINTS -- minimum data points required by kruskalalgorithm.

### How to make change:
You can add algorithm name, different parameters under foremast/blob/[branch]/deploy/foremast/3_judgement/foremast-brain.yaml

You can refer below ES_ENDPOINT as example

```
env:
- name: ES_ENDPOINT
  value: "http://elasticsearch-discovery.foremast.svc.cluster.local:9200"
```




