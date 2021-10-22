#!/bin/bash

dpath='./data/'
path0='./L0/'
for f in `ls $dpath`; do
 sh rmtmp.sh
 echo $dpath$f
 cp $dpath$f $path0
 sh run.sh
done
