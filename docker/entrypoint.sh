#!/bin/sh
set -eu

python manage.py wait_for_db --timeout "${DB_WAIT_TIMEOUT:-60}"

if [ "${DJANGO_RUN_MIGRATIONS:-1}" = "1" ]; then
    python manage.py migrate --noinput
fi

exec "$@"
