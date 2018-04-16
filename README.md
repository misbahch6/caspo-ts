# Caspo-ts (Caspo Time Series)
Caspo-ts is a software to infer Boolean Networks from prior knowledge network and phosphoproteomic time series data. This software is based on Answer Set Programming and Model Checking. 

## Installation:  
### 1) Docker Image   
   * ```docker pull misbahch6/caspo-timeseries```  
     * To install Docker please follow this link: https://docs.docker.com/install/

### 2) Manually  
   * ```git clone https://github.com/misbahch6/caspo-ts.git```  
   * This will install necessary dependencies, except the caspo, gringo python module and NuSMV.
   * To install caspo please use:
     * ```conda install -c bioasp caspo```
        * To install anaconda please follow this link: https://docs.anaconda.com/anaconda/install/
   * To install gringo python module please use:
     * ```conda install -c potassco clingo=4.5.4```
   * To install NuSMV please compile the sources or put the binaries in your /usr/local/bin
     * http://nusmv.fbk.eu

## Format of Commands:  

Here we show the fromat of commands used by the caspo-ts.

### 1) Identify all Boolean Networks:
 
 ```python cli.py identify PKN.sif DATASET.csv RESULTS.csv```    
     
   The option --limit to specify the number of BNs.

### 2) Minimum Square Error (MSE) Calculation:
 
 ```python cli.py mse PKN.sif DATASET.csv```   
     
   The option --network to specify the csv file containing BNs to calculate MSE for them.

### 3) Validation of Boolean Networks through Model Checker:
   
   ```python cli.py validate PKN.sif DATASET.csv RESULTS.csv``` 
   
   This command invokes a model-checker (NuSMV) to calculate true positive BNs. The true      positive rate is then displayed. 

### Note:
* PKN.sif is the SIF description of the PKN delimiting the domain of BNs, e.g.: benchmarks/1/pkn1_cmpr.sif  
* DATASET.csv is the MIDAS description of the multiplex dataset, e.g., benchmarks/1/dataset1_cmpr_bn_1.csv  
* RESULTS.csv is a CSV description of a set of Boolean Networks, as outputted by our python scripts.  
* python is the python interpreter in version 2.7.X. On some systems, you should use python2. 
* Datasets folder contains the ```DREAM 8``` Challenge dataset.

## Usage 

Here we show two examples: One is with artifical dataset and the other is with ```DREAM 8``` challenge data.

If you have installed docker image then start an interactive session by typing:  

```docker run -ti --entrypoint /bin/bash misbahch6/caspo-timeseries``` 

```cd /src```

## Example 1:

The following command will store the set of Boolean Networks in result.csv.

```caspots identify pkn.sif dataset.csv result.csv```
```
start initial solving
initial solve took 0.475992202759
optimizations = [0]
begin enumeration
enumeration took 0.477589845657
54 solution(s) for the over-approximation
```
The following command will display minimum mse. 

```caspots mse pkn.sif dataset.csv --networks result.csv```
```
MSE_discrete = 0.155167584136
MSE_sample >= 0.155167584136
```
The following command will model check over-approximated BNs.

```caspots validate  pkn.sif dataset.csv result.csv```
```
54/54 true positives [rate: 100.00%]
```

## Example 2:

To idenfify 10 BNs for ```BT549``` Cell line:

```caspots identify datasets/Dream8/merge_hpn_cmpr_CS.sif datasets/Dream8/BT549Refined-remove-ready.csv result.csv --limit 10```

```
# start initial solving
# initial solve took 865.829895973
# optimizations = [0]
# begin enumeration
# enumeration took 12.5855491161
10 solution(s) for the over-approximation
```

The argument --limit can be used to specify the number of BNs.

To calculate MSE:

```caspots mse datasets/Dream8/merge_hpn_cmpr_CS.sif datasets/Dream8/BT549Refined-remove-ready.csv --networks result.csv```

```
MSE_discrete = 0.349898336884
MSE_sample >= 0.349898336884
```

To model check learned BNs:

```caspots validate datasets/Dream8/merge_hpn_cmpr_CS.sif datasets/Dream8/BT549Refined-remove-ready.csv result.csv```
