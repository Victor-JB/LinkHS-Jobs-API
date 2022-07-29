import traceback

from flask import Flask
from careerjet_api import CareerjetAPIClient
from flask import request
from json2html import *
import json
from get_full_description import getFullJobDesc

app = Flask(__name__)

# ---------------------------------------------------------------------------- #
@app.route('/search')
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
if __name__ == "__main__":
	# setting debug to True enables hot reload
	# and also provides a debugger shell
	# if you hit an error while running the server
	app.run(debug = True)
