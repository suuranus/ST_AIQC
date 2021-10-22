#!/bin/bash

python 1_sort.py

python 2_caculate.py

python 3_AIQC_xgb.py

python 4_interp_sounding.py

Aspen-QC -i ./L3/L3.eol  -l ./L3_aspen/L3_aspen.eol

python 5_aspen_interp.py

test=$(ls ./L1/ | grep .csv)

cp ./L0/*           ./output/
cp ./L1/*.csv       ./output/$test
cp ./L2/*.csv       ./output/${test/L1.csv/L2.csv}
cp ./L3/*.csv       ./output/${test/L1.csv/L3.csv}
cp ./L4/*.csv       ./output/${test/L1.csv/L4.csv}
cp ./L4_aspen/*.csv ./output/${test/L1.csv/L4_aspen.csv}

cp ./L1/*.txt       ./output/${test/L1.csv/L1_log.txt}
cp ./L3/*.txt       ./output/${test/L1.csv/L3_log.txt}
cp ./L4/*.txt       ./output/${test/L1.csv/L4_log.txt}

cp ./L2/*.eol       ./output/${test/L1.csv/L2.eol}
cp ./L3/*.eol       ./output/${test/L1.csv/L3.eol}
cp ./L4/*.eol       ./output/${test/L1.csv/L4.eol}
cp ./L3_aspen/*.eol ./output/${test/L1.csv/L3_aspen.eol}
cp ./L4_aspen/*.eol ./output/${test/L1.csv/L4_aspen.eol}

chmod 777 output/*
