mysql -u root -e "DROP SCHEMA IF EXISTS ag_dev; CREATE SCHEMA ag_dev DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;"
python ./manage.py migrate
mysql -u root ag_dev < ag/reference/load_from_datamaster.sql
python manage.py loaddata was_initial_data.json
python manage.py generer_invitations_mandates
