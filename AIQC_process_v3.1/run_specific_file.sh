#!/bin/bash

dpath='./data/'
L0_path='./L0/'
L1_path='./L1/'
L2_path='./L2/'
L3_path='./L3/'
L3_aspen_path='./L3_aspen/'

ST_no=$1
#echo $ST_no

target=$(ls $dpath | grep $ST_no)
echo "target file: $dpath$target"

cp $dpath$target $L0_path
echo $target

python 1_sort_spec.py $target

step2_input_file=$(ls $L1_path | grep $ST_no | grep '.csv')
python 2_caculate.py $step2_input_file

step3_input_file=$(ls $L2_path | grep $ST_no | grep '.csv')
python 3_AIQC_xgb.py $step3_input_file

step4_input_file=$(ls $L3_path | grep $ST_no | grep '.csv')
python 4_interp_sounding.py $step4_input_file

ASPEN_input_file=$(ls $L3_path | grep $ST_no | grep '.eol')
Aspen-QC -i $L3_path$ASPEN_input_file  -l $L3_aspen_path${ASPEN_input_file/.eol/_aspen.eol}

step5_input_file=$(ls $L3_aspen_path | grep $ST_no | grep '.eol')
python 5_aspen_interp.py $step5_input_file

cp ./L0/*       ./output/
cp ./L1/*       ./output/
cp ./L2/*       ./output/
cp ./L3/*       ./output/
cp ./L4/*       ./output/
cp ./L3_aspen/* ./output/
cp ./L4_aspen/* ./output/

chmod 777 output/*

echo 'done!'
