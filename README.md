### INF601 - Advanced Programming in Python
### Cooper Weinhold
### Fitness Website Final Project


## Description
This program creates a webpage with the intent of allowing users to input 
information about themselves to achieve their physical fitness goals. After 
taking input from the user the site will display what their macro goals should 
be as well as having a page that gives example exercises to do to help achieve 
the goals.

### Dependencies
```
pip install -r requirements.txt

```

### Executing program

```
cd fitnessSite
python manage.py makemigrations (this will create any SQL entries that need to go into the database)
python manage.py migrate (this will apply the migrations)
python manage.py createsuperuser (this will create the administrator login for your /admin side of your project)
python manage.py runserver
```

### Output
Calculated macro goals, example exercises, and meals.  

## Authors

Cooper Weinhold
cjweinhold@mail.fhsu.edu


## Acknowledgments

Inspiration, code snippets, etc.