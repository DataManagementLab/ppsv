#!/bin/bash
echo "Starting Tests"
..\venv\Scripts\Activate.ps1
cd ../ppsv
coverage run --source='.' manage.py test
coverage report
cd ../utils