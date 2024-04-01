
all: help

serve:
	python3 manage.py runserver

format:
	isort .
	black .

help:
	@echo "No docs/help yet"
