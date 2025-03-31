# Caspo-ts (Caspo Time Series)

Caspo-ts is a software to infer Boolean Networks from prior knowledge networks
and phosphoproteomic time series data. This software is based on Answer Set
Programming and Model Checking.

## Installation

### With conda

```shell
conda create -n caspots-test -c potassco -c bioasp -c colomoto caspo nusmv clingo pip
conda activate caspots-test
pip install git+https://github.com/misbahch6/caspo-ts.git@update-clingo5
```

or simply use the
[env.yml](https://raw.githubusercontent.com/misbahch6/caspo-ts/refs/heads/update-clingo5/env.yml)
file.

```shell
conda env create -f env.yml
conda activate caspots-test
```

## Available Commands

Here we show the available commands offered by the caspo-ts system.

### 1) Identify all Boolean Networks

```
caspots identify PKN.sif DATASET.csv RESULTS.csv
```

This command calculates all BNs for a given prior knowledge network and time
series data. To limit the number of BNs, option `--limit n` can be used.

### 2) Minimum Square Error (MSE) Calculation

```
caspots mse PKN.sif DATASET.csv
```

Option `--networks file` to specify the csv file containing the BNs to
calculate the MSE for.

### 3) Validation of Boolean Networks through Model Checking

```
caspots validate PKN.sif DATASET.csv RESULTS.csv
```

This command invokes a model-checker (NuSMV) to calculate true positive BNs.
The true positive rate is then displayed.

### Notes

- `PKN.sif` is the SIF description of the PKN delimiting the domain of the BNs,
  e.g.: `benchmarks/1/pkn1_cmpr.sif`
- `DATASET.csv` is the MIDAS description of the multiplex dataset, e.g.,
  `benchmarks/1/dataset1_cmpr_bn_1.csv`
- `RESULTS.csv` is a CSV description of a set of Boolean Networks, as outputted
  by our python scripts.
- The `datasets` folder contains the `DREAM 8` Challenge dataset.

## Usage

Here we show two examples: one with artifical data and another with `DREAM 8`
challenge data.

### Example 1

The following command will store the set of Boolean Networks in `result.csv`:

```
caspots identify pkn.sif dataset.csv result.csv

start initial solving
initial solve took 0.475992202759
optimizations = [0]
begin enumeration
enumeration took 0.477589845657
54 solution(s) for the over-approximation
```

The following command will display the minimum mse:

```
caspots mse pkn.sif dataset.csv --networks result.csv

MSE_discrete = 0.155167584136
MSE_sample >= 0.155167584136
```

The following command will model check the over-approximated BNs obtained by
the first call:

```
caspots validate  pkn.sif dataset.csv result.csv

54/54 true positives [rate: 100.00%]
```

### Example 2

To idenfify 10 BNs for the `BT549` cell line:

```
caspots identify datasets/Dream8/merge_hpn_cmpr_CS.sif datasets/Dream8/BT549Refined-remove-ready.csv result.csv --limit 10

# start initial solving
# initial solve took 174.37147617340088
# optimizations = [0]
# begin enumeration
# enumeration took 2.1883344650268555
10 solution(s) for the over-approximation
```

Note that it may take few minutes (about 10 min depending on the machine) to
setup files before starting to enumerate solutions. When it will start solving,
it will display the message `# start initial solving`.

To calculate the MSE:

```
caspots mse datasets/Dream8/merge_hpn_cmpr_CS.sif datasets/Dream8/BT549Refined-remove-ready.csv --networks result.csv

MSE_discrete = 0.3498983368835096
MSE_sample >= 0.3514026055805377
```

To model check the learned BNs:

```
caspots validate datasets/Dream8/merge_hpn_cmpr_CS.sif datasets/Dream8/BT549Refined-remove-ready.csv result.csv

10/10 true positives [rate: 100.00%]
```
