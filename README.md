## Table of Contents
- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installing](#installing)
- [Running the App](#running-the-app)

### Getting Started
To get started, follow the instructions below.

### Prerequisites
To run this project, you will need to have the following installed:
- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [anaconda (optional)](https://www.anaconda.com/download)
- [python: ***3.12***](https://www.python.org/downloads/)

### Installing
To install this project, run the following command in your terminal:
1. Activate the project's virtualenv:
```
pipenv shell
```
Or
```
make start-env
```
2. Install the dependencies
```
pipenv install
```

### Running the App
1. Activate the project's virtualenv, run:
```
pipenv shell
```
Or
```
make start-env
```
2. Start the application
```
python manage.py runserver <PORT>
```
OR
```
make run-server port=<PORT>
```