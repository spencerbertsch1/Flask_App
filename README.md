# Winter Sports Catalog

Keep track of all your winter spots needs with this catalog! From mountain sports to fun on the ice, this catalog contains items associated with
four main snowsport categories.

This site uses CRUD functionality with a SQLite database backend - users can add new items, edit items, view items, and remove items from the catalog.

## Dependencies

- Python 3
- Flask
- httplib2
- SQL Alchemy

## JSON API Endpoints

This app also serves two API endpoints which will return either the categories in the database, or each of the items currently residing in each category.

- Categories in the database: http://localhost:5000/catalog/JSON
- Items in the skiing category: http://localhost:5000/catalog/1/JSON

*Note: Changing the category ID in the URL will return data for different categories.*

## How to get started

1. Install any necessary dependencies using pip or conda.
2. To run the catalog app, you will first need to either clone this repo (if using github) or create a directory containing all of the project files.
3. Navigate to the directory using your terminal and run the database_setup.py file by typing the following: `$ python database_setup.py`
4. Then run `python database_filler.py` to populate the database with a few starter catalog items.
5. Then run `python project.py`
6. Navigate to a local web browser and visit `http://localhost:5000/catalog`

### REFERENCES

The google oauth2 code seen in this file was adapted largely from Udacity's Full Stack Development course. Most of the code in this project was sourced to some extent from that Udacity course.
