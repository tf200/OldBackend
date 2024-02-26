# MAICare

### REQUIREMENTS
- Python 3.12

### SETUP ENVIRONMENT
- Install Python 3.12
`pyenv install 3.12.0`
- Create a virtual environment for the project
`python3 -m venv env`
- Activate the virtual environment
`source env/bin/activate`
- Make sure you are in the root directory of the project

### INSTALL DEPENDENCIES
- Install the dependencies `pip install -r requirements.txt`

### RUN THE APPLICATION
- Run the application `python3 manage.py runserver`

### MIGRATE DATABASE
- run `python3 manage.py makemigrations` to create the migration file
- run `python3 manage.py migrate` to apply the migration
