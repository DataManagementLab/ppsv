# Setup PPSV
"Setup PPSV DEV windows"


# abort on error, print executed commands
$ErrorActionPreference = "Stop"


# Removing old virtualenv
if (Test-Path -Path ..\venv) {
    "Removing old virtualenv"
    Remove-Item -path ..\venv -Recurse
} 


# Setup virtualenv
"Setup virtualenv"
python -m venv ..\venv

# Activate virtualenv
..\venv\Scripts\Activate.ps1

# Updated pip
"`nUpdate pip"
..\venv\Scripts\python.exe -m pip install --upgrade pip


# Install dev requirements
"`nInstall dev requirements"
pip install -r .\requirements_dev.txt

# Setup database
"`nSetup database"
python ..\ppsv\manage.py migrate

# Prepare static files and translations
"`nPrepare static files and translations"
python ..\ppsv\manage.py collectstatic --noinput
python ..\ppsv\manage.py compilemessages -l de_DE

# Create superuser
# Credentials are entered interactively on CLI
"`nCreate superuser"
python ..\ppsv\manage.py createsuperuser



deactivate