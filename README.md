# Caspo-ts (Caspo Time Series)

Caspo-ts is a software to infer Boolean Networks from prior knowledge networks
and phosphoproteomic time series data. This software is based on Answer Set
Programming and Model Checking.

## Installation

There are two alternative ways to install caspo-ts.

### 1) Docker Image

  * To install Docker, please follow this link:
    * <https://docs.docker.com/install/>
  * A container with the caspots system can then be installed with:
    * `docker pull misbahch6/caspots-m`

### 2) Manually

  * To get caspots (without dependencies):
    * `git clone https://github.com/misbahch6/caspo-ts.git`
  * To install anaconda please follow this link:
    * <https://docs.anaconda.com/anaconda/install/>
  * To install caspo please use:
    * `conda install -c bioasp caspo`
  * To install gringo python module please use:
    * `conda install -c potassco clingo=4.5.4`
  * To install NuSMV, please compile the sources and put the binaries in
    `/usr/local/bin`:
    * <http://nusmv.fbk.eu>

## Available Commands

Here we show the available commands offered by the caspo-ts system. If manually
installed caspots from source run it with `python cli.py`. In the docker image
the command `caspots` is available instead.

### 1) Identify all Boolean Networks

    python cli.py identify PKN.sif DATASET.csv RESULTS.csv

This command calculates all BNs for a given prior knowledge network and time
series data. To limit the number of BNs, option `--limit n` can be used.

### 2) Minimum Square Error (MSE) Calculation

    python cli.py mse PKN.sif DATASET.csv

Option `--networks file` to specify the csv file containing the BNs to
calculate the MSE for.

### 3) Validation of Boolean Networks through Model Checking

    python cli.py validate PKN.sif DATASET.csv RESULTS.csv

This command invokes a model-checker (NuSMV) to calculate true positive BNs.
The true positive rate is then displayed.

### Notes

  * `PKN.sif` is the SIF description of the PKN delimiting the domain of the
    BNs, e.g.: `benchmarks/1/pkn1_cmpr.sif`
  * `DATASET.csv` is the MIDAS description of the multiplex dataset, e.g.,
    `benchmarks/1/dataset1_cmpr_bn_1.csv`
  * `RESULTS.csv` is a CSV description of a set of Boolean Networks, as
    outputted by our python scripts.
  * `python` is the python interpreter in version 2.7.X. On some systems, you
    should use `python2`.
  * The `datasets` folder contains the `DREAM 8` Challenge dataset.

## Usage

Here we show two examples: one with artifical data and another with `DREAM 8`
challenge data.

If you have installed docker image then start an interactive session by typing:

    host $ docker run -ti --entrypoint /bin/bash misbahch6/caspo-timeseries
    docker # cd /src

With `host $` we prefix commands that should be executed on the host system and
with `docker #` commands that should be executed in the docker container.

### Example 1

The following command will store the set of Boolean Networks in `result.csv`:

    docker # caspots identify pkn.sif dataset.csv result.csv

    start initial solving
    initial solve took 0.475992202759
    optimizations = [0]
    begin enumeration
    enumeration took 0.477589845657
    54 solution(s) for the over-approximation

The following command will display the minimum mse:

    docker # caspots mse pkn.sif dataset.csv --networks result.csv

    MSE_discrete = 0.155167584136
    MSE_sample >= 0.155167584136

The following command will model check the over-approximated BNs obtained by
the first call:

    docker # caspots validate  pkn.sif dataset.csv result.csv

    54/54 true positives [rate: 100.00%]

### Example 2

To idenfify 10 BNs for the `BT549` cell line:

    docker # caspots identify datasets/Dream8/merge_hpn_cmpr_CS.sif datasets/Dream8/BT549Refined-remove-ready.csv result.csv --limit 10

    # start initial solving
    # initial solve took 865.829895973
    # optimizations = [0]
    # begin enumeration
    # enumeration took 12.5855491161
    10 solution(s) for the over-approximation

Note that it may take few minutes (about 15 min depending on the machine) to
setup files before starting to enumerate solutions. When it will start solving,
it will display the message `# start initial solving`.

To calculate the MSE:

    docker # caspots mse datasets/Dream8/merge_hpn_cmpr_CS.sif datasets/Dream8/BT549Refined-remove-ready.csv --networks result.csv

    MSE_discrete = 0.349898336884
    MSE_sample >= 0.349898336884

To model check the learned BNs:

    docker # caspots validate datasets/Dream8/merge_hpn_cmpr_CS.sif datasets/Dream8/BT549Refined-remove-ready.csv result.csv

    6/10 true positives [rate: 60.00%]

## FAQ

### How to quit docker?

    docker # exit

### How to copy file from docker container to local machine?

    host $ docker cp CONTAINER-ID:SRC_PATH DEST_PATH

For example if you want to copy `result.csv`, open another terminal and type:

    host $ docker ps

This will print the `CONTAINER-ID` of the running docker image, then type:

    host $ docker cp CONTAINER-ID:src/result.csv .

This will copy the file in the current directory.
