
all: help

serve:
	python3 manage.py runserver 0.0.0.0:8000

format:
	isort .
	black .

create_diagram:
	python3 manage.py graph_models -a > diagram.dot

help:
	@echo "No docs/help yet"
