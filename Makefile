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
run-test:
	python manage.py test

# run redis
run-redis:
	docker run -d -p 6379:6379 redis

# store celery worker process
celery-worker:
	celery -A ${name} worker --loglevel=info

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