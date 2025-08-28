#!/bin/bash

input=$1
output=$2
ffmpeg -v warning -i "$input" "$output" && rm "$input"
