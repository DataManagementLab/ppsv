#!/bin/bash
echo "Starting Tests"
alias python=python3
alias pip=pip3
python seminarplatzvergabe/ppsv/manage.py test
