#!/usr/bin/env bash
set -e

function main {
  case "$1" in

    "build" )
      build;;

    "resetdb" )
      if [ "$2" = "--test" ]; then
        killtestdbconnections
        resetdb test
      else
        killdbconnections
        resetdb
      fi;;

    "bt" )
      testbackend;;

    "ut" )
      testjsunit;;

    "ft" )
      testfunctional;;

    "at" )
      testbackend
      testjsunit
      testfunctional;;

    esac
}

function build {
  cd eums/client
  grunt build
  cd -
}

function resetdb {
  if [ "$1" = "test" ]; then
    echo "+++ Resetting database eums_test..."
    echo "drop database eums_test; create database eums_test;" | psql -h localhost -U postgres
    python manage.py migrate --settings=eums.test_settings
    python manage.py loaddata eums/client/test/functional/fixtures/user.json --settings=eums.test_settings
  else
    echo "+++ Resetting database eums..."
    echo "drop database eums; create database eums;" | psql -h localhost -U postgres
    python manage.py migrate
    python manage.py loaddata eums/client/test/functional/fixtures/user.json
  fi
}

function testbackend {
  source eums/bin/activate
  python manage.py test
}

function testjsunit {
  cd eums/client
  grunt unit
  cd -
}

function testfunctional {
  killtestdbconnections
  cd eums/client
  grunt functional
  cd -
}

function killdbconnections {
  echo "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'eums' AND pid <> pg_backend_pid();" | psql &> /dev/null
}

function killtestdbconnections {
  echo "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'eums_test' AND pid <> pg_backend_pid();" | psql &> /dev/null
}

main $@
exit 0