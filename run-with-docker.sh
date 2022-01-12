#!/bin/bash
docker build -t ppsv .
docker run -it --name ppsv -p 8000:8000 ppsv