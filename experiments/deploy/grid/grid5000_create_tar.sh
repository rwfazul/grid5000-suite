#!/bin/bash

HADOOP="$HOME/hadoop"

cd $HADOOP
rm -f hadoop-2.9.2.tar.gz
tar cf - hadoop-2.9.2 | gzip > hadoop-2.9.2.tar.gz