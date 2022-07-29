# flask imports
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid # for public id
from werkzeug.security import generate_password_hash, check_password_hash
# imports for PyJWT authentication
import jwt
from datetime import datetime, timedelta
from functools import wraps

# import(s) for .env management
import os

# other imports
import traceback
from careerjet_api import CareerjetAPIClient
from json2html import *
import json
from get_full_description import getFullJobDesc

# creates Flask object
app = Flask(__name__)

# configuration
# NEVER HARDCODE YOUR CONFIGURATION IN YOUR CODE
# INSTEAD CREATE A .env FILE AND STORE IN IT (USING API_KEY AS VARIABLE NAME)
app.config['SECRET_KEY'] = os.getenv('API_KEY')
# database name
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# creates SQLALCHEMY object
db = SQLAlchemy(app)

# ---------------------------------------------------------------------------- #
# Database ORMs
class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	public_id = db.Column(db.String(50), unique = True)
	name = db.Column(db.String(100))
	email = db.Column(db.String(70), unique = True)
	password = db.Column(db.String(80))

# ---------------------------------------------------------------------------- #
# decorator for verifying the JWT
def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None
		# jwt is passed in the request header
		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']
		# return 401 if token is not passed
		if not token:
			return jsonify({'message' : 'Token is missing !!'}), 401

		try:
			# decoding the payload to fetch the stored details
			data = jwt.decode(token, app.config['SECRET_KEY'])
			current_user = User.query\
				.filter_by(public_id = data['public_id'])\
				.first()
		except:
			return jsonify({
				'message' : 'Token is invalid !!'
			}), 401
		# returns the current logged in users contex to the routes
		return f(current_user, *args, **kwargs)

	return decorated

# ---------------------------------------------------------------------------- #
@app.route('/search')
@token_required
def search():
    cj = CareerjetAPIClient("en_US")
    location = request.args.get('location')
    keywords = request.args.get('keywords')
    pageNum = request.args.get('page')
    response = 'Bad Request'

    if keywords is not None or location is not None:
        result_json = cj.search({
            'location': location,
            'keywords': keywords,
            'affid': '5f41b19494be1f6eaab8a755b612e343',
            'user_ip': '11.22.33.44',
            'url': 'http://www.example.com/jobsearch?q=python&l=london',
            'user_agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0',
            'pagesize': '99',
            'page': pageNum,
        })

        print(len(result_json['jobs']))
        print(type(result_json))

        try:
            """
            desc = getFullJobDesc(result_json)
            if type(desc) != list:
                raise ValueError('Returned description is not of type list')
            i = 1
            for element in result_json['jobs']:
                element['description'] = desc[i - 1]
                i += 1
            """
            response = json.dumps(result_json)
        except Exception as e:
            traceback.print_exc()
            response = {"title": "Error Code 1 (No Jobs Available)"}

    return response

# ---------------------------------------------------------------------------- #
# User Database Route
# this route sends back list of users
@app.route('/user', methods =['GET'])
@token_required
def get_all_users(current_user):
	# querying the database
	# for all the entries in it
	users = User.query.all()
	# converting the query objects
	# to list of jsons
	output = []
	for user in users:
		# appending the user data json
		# to the response list
		output.append({
			'public_id': user.public_id,
			'name' : user.name,
		})

	return jsonify({'users': output})

# ---------------------------------------------------------------------------- #
# route for logging user in
@app.route('/login', methods =['POST'])
def login():
	# creates dictionary of form data
	auth = request.form

	if not auth or not auth.get('email') or not auth.get('password'):
		# returns 401 if any email or / and password is missing
		return make_response(
			'Could not verify',
			401,
			{'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
		)

	user = User.query\
		.filter_by(email = auth.get('email'))\
		.first()

	if not user:
		# returns 401 if user does not exist
		return make_response(
			'Could not verify',
			401,
			{'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
		)

	if check_password_hash(user.password, auth.get('password')):
		# generates the JWT Token
		token = jwt.encode({
			'public_id': user.public_id,
			'exp' : datetime.utcnow() + timedelta(minutes = 30)
		}, app.config['SECRET_KEY'])

		return make_response(jsonify({'token' : token.decode('UTF-8')}), 201)
	# returns 403 if password is wrong
	return make_response(
		'Could not verify',
		403,
		{'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
	)

# ---------------------------------------------------------------------------- #
# signup route
@app.route('/signup', methods =['POST'])
def signup():
	# creates a dictionary of the form data
	data = request.form

	# gets name, email and password
	name, email = data.get('name'), data.get('email')
	password = data.get('password')

	# checking for existing user
	user = User.query\
		.filter_by(email = email)\
		.first()
	if not user:
		# database ORM object
		user = User(
			public_id = str(uuid.uuid4()),
			name = name,
			email = email,
			password = generate_password_hash(password)
		)
		# insert user
		db.session.add(user)
		db.session.commit()

		return make_response('Successfully registered.', 201)
	else:
		# returns 202 if user already exists
		return make_response('User already exists. Please Log in.', 202)

# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
	# setting debug to True enables hot reload
	# and also provides a debugger shell
	# if you hit an error while running the server
	app.run(debug = True)
