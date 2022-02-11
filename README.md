# Seminarplatzvergabe

Bachelor Praktikum Thema 06 Seminarplatzvergabe

<h2>Run Tests</h2>
`sh tests/test.sh`

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

# PPSV

## Description
PPSV is a platform for students to select and manage their topics in courses like seminars or practica. Additionally, students are able to do this alone or in selfmade groups.

## Setup
This repository contains a Django project with several apps.

### Requirements
PPSV has two types of requirements: System requirements are dependent on the operating system and need to be installed manually beforehand. Python requirements will be installed inside a virtual environment (strongly recommended) during a setup.

#### System Requirements
* Python 3.7+ incl. development tools
* Virtualenv

#### Python Requirements
Python requirements are listed in `requirements.txt`. They can be installed with pip using `-r requirements.txt`

### Development Setup

* Create a new directory that should contain the files in the future, e.g. ``mkdir seminarplatzvergabe``
* Change into that directory ``cd seminarplatzvergabe``
* Clone this repository ``git clone URL .``

#### Linux

**Manual Setup**

1. Set up a virtual environment using the proper python version `virtualenv venv -p python3`
1. Activate virtualenv `source venv/bin/activate`
1. Install python requirements `pip install -r requirements.txt`
1. Set up necessary database tables etc. `python manage.py migrate`
1. Setup initial revision for all registered models for versioning `python manage.py createinitialrevisions`
1. Compile translations `python manage.py compilemessages`
1. Create a privileged user, credentials are entered interactively on CLI `python manage.py createsuperuser`
1. Deactivate virtualenv `deactivate`

**Development Server**

To start the application for development use `python manage.py runserver` from the project directory.
*Do not use this for deployment!*

In your browser, access `http://127.0.0.1:8000/` and continue from there.

#### Windows

**Manual Setup**

1. Set up a virtual environment using the proper python version virtualenv venv -p python3`
1. Activate virtualenv `.\venv\Scripts\activate`
1. Install python requirements `pip install -r requirements.txt`
1. Set up necessary database tables etc. `python manage.py migrate`
1. Setup initial revision for all registered models for versioning`python manage.py createinitialrevisions`
1. Prepare static files (can be omitted for dev setups) `python manage.py collectstatic`
1. Compile translations `python manage.py compilemessages`
1. Create a privileged user, credentials are entered interactively on CLI `python manage.py createsuperuser`
1. Deactivate virtualenv `deactivate`

**Development Server**

To start the application for development use `python manage.py runserver` from the project directory.
*Do not use this for deployment!*

In your browser, access `http://127.0.0.1:8000/` and continue from there.

### Deployment Setup

This application can be deployed using a web server as any other Django application.
Remember to use a secret key that is not stored in any repository or similar, and disable DEBUG mode (`settings.py`).

**Step-by-Step Instructions**

1. Log into your system with a sudo user
1. Install system requirements
1. Create a folder, e.g. `mkdir /srv/seminarplatzvergabe/`
1. Change to the new directory `cd /srv/seminarplatzvergabe/`
1. Clone this repository `git clone URL .`
1. Set up a virtual environment using the proper python version `virtualenv venv -p python3`
1. Activate virtualenv `source venv/bin/activate`
1. Update tools `pip install --upgrade setuptools pip wheel`
1. Install python requirements `pip install -r requirements.txt`
1. Install postgres 
1. Create postgres user and database and grant rights (insert suitable names for username and dbname)
   * sudo -u postgres createuser username
   * sudo -u postgres createdb dbname
   * sudo -u postgres psql 
   * psql=# alter user <username> with encrypted password '<password>'; 
   * psql=# grant all privileges on database <dbname> to <username> ;
1. Create the file ``ppsv/settings_secrets.py`` (copy from ``settings_secrets.py.sample``) and fill it with the necessary secrets (e.g. generated by ``tr -dc 'a-z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c50``) (it is a good idea to restrict read permissions from others)
Set the host in the file as `HOSTS = ['*']`
    If necessary enable uwsgi proxy plugin for Apache e.g.``a2enmod proxy_uwsgi``
1. Edit the apache config to serve the application and the static and media files, e.g. on a dedicated system in `/etc/apache2/sites-available/000-default.conf` within the `VirtualHost` tag add:

    ```
    Alias /static /srv/seminarplatzvergabe/ppsv/static
    <Directory /srv/seminarplatzvergabe/ppsv/static>
      Require all granted
    </Directory>

    Alias /media /srv/seminarplatzvergabe/ppsv/media
    <Directory /srv/seminarplatzvergabe/ppsv/media>
      Require all granted
    </Directory>

    ProxyPassMatch ^/media/ !
    ProxyPassMatch ^/static/ !
    ProxyPass / uwsgi://127.0.0.1:3035/
    ```
    or create a new config (.conf) file (similar to ``apache-seminarplatzvergabe.conf``) replacing $SUBDOMAIN with the subdomain the system should be available under, and $MAILADDRESS with the e-mail address of your administrator and $PATHTO with the appropriate paths. Copy or symlink it to `/etc/apache2/sites-available`. Then activate it with `a2ensite apache-seminarplatzvergabe`.
    
1. Restart Apache `sudo apachectl restart`
1. Create a dedicated user, e.g. `adduser django --disabled-login`
1. Transfer ownership of the folder to the new user `chown -R django:django /srv/seminarplatzvergabe`
1. Make sure your `wsgi.py` looks like this
    ```
    import os, sys

    from django.core.wsgi import get_wsgi_application

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_production")
    
    sys.path.append('srv/seminarplatzvergabe/ppsv/ppsv')

    application = get_wsgi_application()
    ```
    and change the `ppsv.settings` in the `manage.py` to `ppsv.settings_production`
1. Copy or symlink the uwsgi config in `uwsgi-seminarplatzvergabe.ini`` to ``/etc/uwsgi/apps-available/` and then symlink it to `/etc/uwsgi/apps-enabled/` using e.g., `ln -s /srv/seminarplatzvergabe/uwsgi-collab-coursebook.ini /etc/uwsgi/apps-available/seminarplatzvergabe.ini` **and** `ln -s /etc/uwsgi/apps-available/seminarplatzvergabe.ini /etc/uwsgi/apps-enabled/seminarplatzvergabe.ini`
1. Test your uwsgi configuration file with `uwsgi --ini uwsgi-seminarplatzvergabe.ini` It should contain the following lines:
    ```
    chdir = /srv/seminarplatzvergabe/ppsv
    wsgi-file = ppsv/wsgi.py
    env = DJANGO_SETTINGS_MODULE=ppsv.settings_production
    ```

1. Restart uwsgi `sudo systemctl restart uwsgi`
1. Prepare static files `python manage.py collectstatic`
1. Execute the update script `./utils/update.sh --prod`
1. If not already active on that server, obtain an SSL certificate, e.g., through [Let's Encrypt](https://certbot.eff.org/lets-encrypt/)
    
## Structure

This repository contains a Django project called seminarplatzvergabe. The functionality is encapsulated into Django apps:

1. **course**: This app contains the general Django models used to represent courses, students, etc.
1. **frontend**: This app provides everything the users see when interacting with the platform
1. **ppsv**: This directory contains basic settings.
