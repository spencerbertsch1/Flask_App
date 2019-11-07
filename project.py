# -*- coding: utf-8 -*-
"""
The google oauth2 code seen in this file was adapted largely from Udacity's
Full Stack Development course. Most of the code in this project was sourced
to some extent from that Udacity course.
"""
# Imports
from flask import (Flask, render_template, request, redirect, jsonify,
                   url_for, flash)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import os

from database_setup import Base, Category, CategoryItem, User

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

# engine = create_engine('sqlite:///WinterSports.db')
engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = engine


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    print('======= LOGIN SESSION:', login_session)

    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect', methods=['GET', 'POST'])
def gdisconnect():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        # flash('You have been successfully logged out')
        # return redirect(url_for('showCatalog'))
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


"""
******************** JSON API Endpoints ********************
"""


# Returns all categories in the database
@app.route('/catalog/JSON')
def catalogJSON():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# Returns all items in a given category
@app.route('/catalog/<int:category_id>/JSON')
def categoryJSON(category_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    items = session.query(CategoryItem).filter_by(
        category_id=category_id).all()
    return jsonify(CategoryItems=[i.serialize for i in items])


# Returns a single specified item
@app.route('/catalog/<int:category_id>/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    items = session.query(CategoryItem).filter_by(
        category_id=category_id).all()
    item = items[item_id]
    return jsonify(CategoryItems=[item.serialize])


"""
******************** Web Pages ********************
"""


# Web Page #1 - Catalog Homepage - simply shows all categories in the catalog
@app.route('/')
@app.route('/catalog')
def showCatalog():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    return render_template('catalog.html', categories=categories)


# Web Page #2 - Show all the items in a category
@app.route('/catalog/<int:category_id>')
def showCategories(category_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CategoryItem).filter_by(category_id=category.id)
    return render_template('categories.html',
                           category=category, items=items)


# Web Page #3 - Show info for one item
@app.route('/catalog/<string:category_id>/category/<string:item_id>/item')
def showItem(category_id, item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    return render_template('item.html', category=category,
                           category_id=category_id, item=item)
    # restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem


# Add an item to a given category
@app.route('/catalog/<string:category_id>/new', methods=['GET', 'POST'])
def addItem(category_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        newItem = CategoryItem(name=request.form['name'],
                               description=request.form['description'],
                               category_id=category_id,
                               user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Item Successfully Created')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('addItem.html', category_id=category_id)


# Edit an item to a given category
@app.route('/catalog/<string:category_id>/item/<string:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    # check if the user is the owner before edits are made
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    owner = getUserInfo(item.user_id)
    if owner.id != login_session['user_id']:
        flash('You do not have access to edit items.')
        return redirect(url_for('showCatalog'))
    editedItem = session.query(CategoryItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        # if request.form['category']:
        #     editedItem.category_id = request.form['category']
        session.add(editedItem)
        session.commit()
        flash("Item successfully edited!")
        return redirect(url_for('showCatalog'))
    else:
        return render_template('editItem.html', item=editedItem,
                               category_id=category_id, item_id=item_id)


# Delete an item to a given category
@app.route('/catalog/<string:category_id>/<string:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
    if itemToDelete.user_id != login_session['user_id']:
        flash('You do not have access to delete this item.')
        return redirect(url_for('showCatalog'))
    category = session.query(Category).filter_by(id=category_id).one()
    # itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Item successfully deleted!")
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteItem.html', category=category,
                               item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
