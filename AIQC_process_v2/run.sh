#!/bin/bash

python 1_sort.py

python 2_caculate.py

python 3_AIQC.py

python 4_interp_sounding.py

python 5_L3toaspen.py

Aspen-QC -i ./L3pr/L3pr.csv  -e ./L3_aspen/L3_aspen.csv

python 6_aspenOP2csv.py

test=$(ls  ./L0)
cp ./L0/*           ./output/
cp ./L1/*.csv       ./output/${test/.csv/_L1.csv}
cp ./L2/*.csv       ./output/${test/.csv/_L2.csv}
cp ./L3/*.csv       ./output/${test/.csv/_L3.csv}
cp ./L4/*.csv       ./output/${test/.csv/_L4.csv}
cp ./L3pr/*.csv     ./output/${test/.csv/_L3pr.csv}
cp ./L3_aspen/*.csv ./output/${test/.csv/_L3_aspen.csv}
cp ./L4pr/*.csv     ./output/${test/.csv/_L4pr.csv}

cp ./L1/*.txt       ./output/${test/.csv/_L1_log.txt}
cp ./L3/*.txt       ./output/${test/.csv/_L3_log.txt}
cp ./L4/*.txt       ./output/${test/.csv/_L4_log.txt}



