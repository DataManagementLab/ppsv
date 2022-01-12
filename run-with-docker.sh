#!/bin/bash
docker build -t ppsv .
docker run -it --name ppsv --network=host ppsv