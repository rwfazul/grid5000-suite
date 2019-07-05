#!/bin/bash

HADOOP_FOLDER=$HOME/hadoop/

mkdir -p $HADOOP_FOLDER
wget --no-dns-cache --no-cache https://apache.mirrors.benatherton.com/hadoop/common/hadoop-2.9.2/hadoop-2.9.2.tar.gz -P $HADOOP_FOLDER
(cd $HADOOP_FOLDER && tar -xvzf $HADOOP_FOLDER/hadoop-2.9.2.tar.gz)
cp $HADOOP_FOLDER/hadoop-2.9.2/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-2.9.2-tests.jar $HADOOP_FOLDER/
mv $HADOOP_FOLDER/hadoop-2.9.2.tar.gz $HADOOP_FOLDER/hadoop-2.9.2_raw.tar.gz
easy_install --user execo
cd ~
wget https://github.com/mliroz/hadoop_g5k/archive/master.zip
unzip master.zip
rm master.zip
mv hadoop_g5k-master/ hadoop_g5k/ 
cd hadoop_g5k
python setup.py install --user