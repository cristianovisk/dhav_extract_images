#!/bin/bash

for file in `ls images/*.dd`;
do
    ./extract.py $file;
done