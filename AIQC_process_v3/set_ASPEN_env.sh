#!/bin/bash

read -p 'Where is the AIQC_process dir at? (abs path):' dir_path

echo $dir_path\AIQC_process

echo '' >>.bashrc
echo '' >>.bashrc
echo '#==========ASPEN setting==========' >>.bashrc
echo '' >>.bashrc
echo 'export PATH='$dir_path'AIQC_process/ASPEN/bin:$PATH' >>.bashrc
echo 'export LD_LIBRARY_PATH='$dir_path'AIQC_process/ASPEN/lib:$LD_LIBRARY_PATH' >>.bashrc
echo '' >>.bashrc
echo '#================================' >>.bashrc


source .bashrc

