#!/bin/bash

echo "this will overwrite the modifications in HDFS Balancer source code..."
read -p  "---> are you sure (y/n)? " opt

if [ "${opt,,}" == "y" ] || [ "${opt,,}" == "yes" ]; then
	SOURCE=../../balancer
	BALANCER_PATH=~/Desktop/hadoop-rel-release-2.9.2/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer
	cp $SOURCE/*.java $BALANCER_PATH
else
	echo -e "\n--> Nothing done!!"
fi