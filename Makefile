# Create virtual env using pipenv

# using pipenv env
start-env:
	pipenv shell

# create project
create-project:
	django-admin startproject $(project_name) .

# run server
run-server-dev:
	python manage.py runserver $(port)

run-server-prod:
	gunicorn doorable.wsgi

# start app
start-app:
	python manage.py startapp $(app_name)

# run test
run-test:
	python manage.py test

# run redis
run-redis:
	docker run -p 6379:6379 --name=doorable-redis redis

# store celery worker process
celery-worker:
	celery -A ${name} worker --loglevel=info

# running flower: monitoring celery worker
monitor-worker:
	celery -A ${name} flower

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