#!/bin/bash
echo "Starting Tests"
sudo python3 ./ppsv/manage.py test --parallel 4
