# Update ppsv on a production server
# changed files need to be copied to the server before executing the script
# Don't overwrite manage.py!

# abort on error, print executed commands
set -ex

# activate virtualenv if necessary
if [ -z ${VIRTUAL_ENV+x} ]; then
  source venv/bin/activate
fi

export DJANGO_SETTINGS_MODULE=ppsv.settings_production

# before potentially breaking anything, create a data backup
mkdir -p backups/
./ppsv/manage.py dumpdata --indent=2 > "backups/$(date +"%Y%m%d%H%M")_datadump.json" --traceback

git pull
pip install --upgrade setuptools pip wheel
pip install --upgrade -r requirements.txt

./ppsv/manage.py migrate
./ppsv/manage.py collectstatic --noinput

touch ppsv/ppsv/wsgi.py
