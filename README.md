# caspo-ts (Caspo Time Series)
Docker Image:
docker pull misbahch6/caspo-ts
docker run misbahch6/caspo-ts


In the following, we assume that

PKN.sif is the SIF description of the PKN delimiting the domain of BNs, e.g.: benchmarks/1/pkn1_cmpr.sif
DATASET.csv is the MIDAS description of the multiplex dataset, e.g., benchmarks/1/dataset1_cmpr_bn_1.csv
RESULTS.csv is a CSV description of a set of Boolean Networks, as outputted by our python scripts.
python is the python interpreter in version 2.7.X. On some systems, you should use python2.

To identify all Boolean Networks, call

caspots identify PKN.sif DATASET.csv RESULTS.csv
By default, the identification will return the subset-minimal BNs. Add --family all to compute all the BNs. Add --family mincard to compute the cardinal-minimal BNs.

The option --true-positives invokes a model-checker (NuSMV) to ensure that only true positive BNs are returned. The true positive rate is then displayed. If the PKN is not compatible with the data, the estimated difference of MSE with minimal MSE is displayed.

The minimal estimated MSE is obtained with

caspots mse PKN.sif DATASET.csv

The option --check-exacts invokes a model-checker (NuSMV) until it finds a BN and a trace with the estimated MSE: in such a case, the displayed MSE is the actual minimal MSE of the PKN with respect to the dataset.
