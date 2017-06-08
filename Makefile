run:
	python manage.py runserver

list_pg_backups:
	heroku pg:backups --app rldm

show_pg_backup_schedule:
	heroku pg:backups:schedules --app rldm

download_pg_backup:
	curl -o latest.dump `heroku pg:backups public-url --app rldm`

restore_pg_backup:
	pg_restore --verbose --clean --no-acl --no-owner -h localhost -U pushkar -d rlfall2016 latest.dump

sync_with_stage:
	heroku pg:backups:restore rldm::$(DB_ID) DATABASE_URL --app rldm-stage

checkout-master:
	git checkout master
	git pull origin master
	git branch -D staging
	git branch staging
	git checkout staging