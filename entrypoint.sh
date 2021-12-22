#!/bin/bash --login
# The --login ensures the bash configuration is loaded,
# enabling Conda.
# Enable strict mode.
set -euo pipefail
# ... Run whatever commands ...

# Temporarily disable strict mode and activate conda:
set +euo pipefail
conda activate django

# Re-enable strict mode:
set -euo pipefail



# echo "Waiting for MySql to start..."
#./wait-for db:3306
#crond  -l 8
python manage.py makemigrations  --noinput
python manage.py migrate --noinput

#python manage.py initadmin
# exec the final command:
# exec python manage.py runserver 9001
python manage.py collectstatic --no-input
python manage.py process_tasks & 
python manage.py runserver 0.0.0.0:80
#gunicorn storefront.wsgi:application --bind 0.0.0.0:80
