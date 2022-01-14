# Seminarplatzvergabe

Bachelor Praktikum Thema 06 Seminarplatzvergabe

<h2>Description</h2>
This is a test description. What could this readme file be used for?
Maybe a description

<h2>Current State</h2>
<p>after steps of Tutorial 2</p>
https://docs.djangoproject.com/en/3.2/intro/tutorial03/

<h2>Run with Docker</h2>
1. Install docker if not installed already
2. Execute `sh run-with-docker.sh`

<h2>Open Questions</h2>
chown django:django -R .

<p> django admin show field only if checkbox is false
https://www.titanwolf.org/Network/q/e686282b-5707-4db0-b095-c615c2a0fed4/y
</p>
<h2>User Story Ideas</h2>
<p>add update.sh
update script need following commands (paths not correct yet)
chown django:django -R .
if [ -z ${VIRTUAL_ENV+x} ]; then
    source virtualenv/bin/activate
fi
if [ "$1" = "--prod" ]; then # if-clause may be unnecessary
    export DJANGO_SETTINGS_MODULE=ppsv.settings_production
fi
pip install --upgrade setuptools pip wheel
pip install --upgrade -r requirements.txt

./manage.py migrate
./manage.py collectstatic --noinput
touch ppsv/wsgi.py
</p>
<p>deal with timezones
https://docs.djangoproject.com/en/3.2/topics/i18n/timezones/
</p>
<p>add translation
https://docs.djangoproject.com/en/3.2/topics/i18n/translation/
</p>
