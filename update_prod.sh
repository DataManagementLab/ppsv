# Update ppsv on a production server
# changed files need to be copied to the server before executing the script
# Don't overwrite manage.py!

# abort on error, print executed commands
set -ex

# activate virtualenv if necessary
if [ -z ${VIRTUAL_ENV+x} ]; then
  source venv/bin/activate
fi

git pull
pip install --upgrade setuptools pip wheel
pip install --upgrade -r requirements.txt

export DJANGO_SETTINGS_MODULE=ppsv.settings_production

./ppsv/manage.py migrate
./ppsv/manage.py collectstatic --noinput

touch ppsv/ppsv/wsgi.py
