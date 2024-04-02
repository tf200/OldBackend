
.PHONY: clean format all help

all: help

serve:
	python3 manage.py runserver 0.0.0.0:8000

format:
	isort .
	black .

create_diagram:
	mkdir -p diagrams
	python3 manage.py graph_models -a > diagrams/diagram.dot
	dot -T pdf diagrams/diagram.dot -o diagrams/diagram.pdf

clean:
	rm -fr diagrams

help:
	@echo "No docs/help yet"
