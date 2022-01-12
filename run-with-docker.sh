#!/bin/bash
docker build -t ppsv .
docker run -it --rm --name ppsv --network=host ppsv