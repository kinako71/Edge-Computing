#!/bin/bash
files=($(ls -tr ./data_temp))
count=${#files[@]}
for ((i=0; i<count-1; i++)); do
    data=/home/jetson/record/data_temp/"${files[i]}"
    # python3 /home/jetson/Bird-Song-Detector/Code/predict_on_audio.py $data
    rm $data
done
# data=/home/jetson/record/data_temp/2025-08-06_09-26-40.wav
# python3 /home/jetson/Bird-Song-Detector/Code/predict_on_audio.py $data
# rm $data