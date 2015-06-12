#!/bin/bash

pgVersion=$1

set -e

cd /opt/app/eums

#Replace pg config file to allow postgres to log in locally
cp scripts/packaging/pg_hba.conf /etc/postgresql/$pgVersion/main/pg_hba.conf
su - postgres -c "/etc/init.d/postgresql start"

#Give pg time to start up
sleep 30s

#setup the database
createuser -U postgres -s -r -w root
createdb -U postgres -O postgres eums 
virtualenv /opt/app/eums/.virtualenvs/eums
source /opt/app/eums/.virtualenvs/eums/bin/activate
pip install -r requirements.txt
python manage.py syncdb --noinput
python manage.py migrate
python manage.py loaddata eums/fixtures/new-deployment-instance.json

su - postgres -c "/etc/init.d/postgresql stop"

#sleep 4
