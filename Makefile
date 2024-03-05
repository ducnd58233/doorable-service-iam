# Create virtual env using pipenv

# using pipenv env
start-env:
	pipenv shell

# create project
create-project:
	django-admin startproject $(project_name) .

# run server
run-server:
	python manage.py runserver $(port)

# start app
start-app:
	python manage.py startapp $(app_name)

# run test
start-app:
	python manage.py test

# migration
migrate:
	python manage.py makemigrations
	python manage.py migrate

revert-migrate:
	python manage.py migrate $(app_name) $(migration_name)

# create superuser to use admin site
create-superuser:
	python manage.py createsuperuser

# change password of superuser
change-superuser-password:
	python manage.py changepassword $(username)