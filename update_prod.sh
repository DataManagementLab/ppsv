# Update ppsv on a production server
# changed files need to be copied to the server before executing the script
# Don't overwrite manage.py!

# abort on error, print executed commands
set -ex

# activate virtualenv if necessary
if [ -z ${VIRTUAL_ENV+x} ]; then
  source virtualenv/bin/activate
fi

pip install --upgrade setuptools pip wheel
pip install --upgrade -r requirements.txt

./ppsv/manage.py migrate
./ppsv/manage.py collectstatic --noinput

touch ppsv/ppsv/wsgi.py
