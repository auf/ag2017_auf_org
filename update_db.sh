set -e

python ./manage.py migrate
python manage.py dbshell < ag/reference/load_from_datamaster.sql
python manage.py dbshell < sql/views.sql
python manage.py loaddata was_initial_data.json
