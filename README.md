# Liine Take Home Assessment

This app provides an endpoint to search Raleigh area restaurants by a datetime date string in the format `%Y-%m-%d %H:%M:%S.%f` and returns a list of restaurants open at the provided time. The data is provided in `liine/restaurants/data/restaurants.csv`.

To run the app:

1. Clone the repository
2. Run `docker build -t restaurant_liine .`
3. Run `docker run -it -p 8000:8000 restaurant_liine`
4. Open your browser and navigate to `http://0.0.0.0:8000/`
5. Enter a python datetime as a string in the format `%Y-%m-%d %H:%M:%S.%f` and click the submit button

To run locally:

1. Clone the repository
2. Build a virtual environment with python 3.9.10
3. Run `pip install -r requirements.txt`
4. Run `python manage.py migrate`
5. Run `python manage.py loaddata --local`
6. Run `python manage.py runserver`
7. Open your browser and navigate to `http://127.0.0.1:8000/`
8. Enter a python datetime as a string in the format `%Y-%m-%d %H:%M:%S.%f` and click the submit button