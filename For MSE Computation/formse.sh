
import os
#!/bin/bash
# My first script

for i in test*.csv
do
#echo $1
output=$(python cli.py mse --networks BT20-BNs.csv merge_hpn_cmpr.sif $i)
echo ${output} >> file.txt
done

