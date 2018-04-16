# Caspo-ts (Caspo Time Series)
Caspo-ts is a software to infer Boolean Networks from prior knowledge network and phosphoproteomic time series data. This software is based on Answer Set Programming and Model Checking. 

## Installation:  
### 1) Docker Image   
   * docker pull misbahch6/caspo-ts   

### 2) Manually through github  
   * git clone https://github.com/misbahch6/caspo-ts.git  
   * This will install necessary dependencies, except the caspo, gringo python module and NuSMV.
   * To install caspo please use:
     * conda install -c bioasp caspo
   * To install gringo python module please use:
     * conda install -c potassco clingo=4.5.4
   * To install NuSMV please compile the sources or put the binaries in your /usr/local/bin
     * http://nusmv.fbk.eu

## Usage:  
### 1) Identify all Boolean Networks:
   * Using Docker Image:
     * docker run misbahch6/caspo-ts identify PKN.sif DATASET.csv RESULTS.csv   
   * Using Manual Installation please run following command from the project's root directory:
     * python cli.py identify PKN.sif DATASET.csv RESULTS.csv    
     
   By default, the identification will return the subset-minimal BNs. Add --family all to compute all the BNs. Add --family      mincard to compute the cardinal-minimal BNs.
   The option --true-positives invokes a model-checker (NuSMV) to ensure that only true positive BNs are returned. The true      positive rate is then displayed. If the PKN is not compatible with the data, the estimated difference of MSE with minimal    MSE is displayed.

### 2) MSE Calculation:
   * Using Docker Image:
     * docker run misbahch6/caspo-ts mse PKN.sif DATASET.csv
   * Using Manual Installation please run following command from the project's root directory:
     * python cli.py mse PKN.sif DATASET.csv   
     
   The option --check-exacts invokes a model-checker (NuSMV) until it finds a BN and a trace with the estimated MSE: in such    a case, the displayed MSE is the actual minimal MSE of the PKN with respect to the dataset.

### 3) Validation of Boolean Networks through Model Checker:
   * Using Docker Image:
     * docker run misbahch6/caspo-ts validate PKN.sif DATASET.csv RESULTS.csv 
   * Using Manual Installation please run following command from the project's root directory:
     * python cli.py validate PKN.sif DATASET.csv RESULTS.csv 
   
## Note:
* PKN.sif is the SIF description of the PKN delimiting the domain of BNs, e.g.: benchmarks/1/pkn1_cmpr.sif  
* DATASET.csv is the MIDAS description of the multiplex dataset, e.g., benchmarks/1/dataset1_cmpr_bn_1.csv  
* RESULTS.csv is a CSV description of a set of Boolean Networks, as outputted by our python scripts.  
* python is the python interpreter in version 2.7.X. On some systems, you should use python2.  
* Dataset folder contain the Dream 8 challenge data. 
