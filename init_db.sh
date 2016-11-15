set -e

mysql -u root -e "DROP SCHEMA IF EXISTS $1; CREATE SCHEMA $1 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;"
python ./manage.py migrate
python manage.py dbshell < ag/reference/load_from_datamaster.sql
python manage.py dbshell < sql/views.sql
python manage.py loaddata was_initial_data.json
python manage.py loaddata auth_user.json
python manage.py loaddata cms_data.json
python manage.py generer_invitations_mandates
