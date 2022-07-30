
# flask imports
from flask import Flask, request

# json formatting imports
from json2html import *
import json
import pandas as pd

# careerjet import
from careerjet_api import CareerjetAPIClient

# google jobs import
from serpapi import GoogleSearch

# retrieve env
import os

import traceback
from get_full_description import getFullJobDesc

app = Flask(__name__)

# ---------------------------------------------------------------------------- #
def get_google_jobs(keywords, location, pageNum):

    if pageNum:
        pageNum = str(int(pageNum) * 10)
    else:
        pageNum = 0

    # search parameters
    params = {
        "engine": "google_jobs",
        "q": keywords,
        "location": location,
        "api_key": os.getenv('SERPAPI_KEY'),
        "start": pageNum
    }

    # connect to Google Jobs API
    client = GoogleSearch(params)
    results = client.get_dict()

    if results['search_metadata']['status'] != 'Success':
        results = 'Search failed'

    else:
        del results['search_metadata']

    return results

# ---------------------------------------------------------------------------- #
def get_careerjet_jobs(keywords, location, pageNum):

    try:
        # initializing the CareerJet client
        cj = CareerjetAPIClient("en_US")

        if pageNum:
            pageNum = str(int(pageNum) + 1)

        # building & sending the API call
        if keywords is not None or location is not None:
            result_dict = cj.search({
                'location': location,
                'keywords': keywords,
                'affid': os.getenv('CAREERJET_AFFID'),
                'user_ip': '11.22.33.44',
                'url': 'http://www.example.com/jobsearch?q=python&l=london',
                'user_agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0',
                'pagesize': '99',
                'page': pageNum,
            })

    except Exception as e:
        return {'title': f'Error Code 2: API query failed. Failed to retrieve jobs from CareerJet API with info: loc={location}, keywords={keywords}, pageNum={pageNum}'}
        traceback.print_exc()

    # testing
    if type(result_dict) is dict:
        if result_dict['type'] == 'LOCATIONS':
            return {'title': "Error Code 4: CareerJet response type is not 'JOBS'"}
        if result_dict['hits'] == 0:
            return {"title": "Error Code 1 (No Jobs Available)"}
    else:
        return {'title': f'Error Code 3: CareerJet API response did not pass testing. Response: {result_dict}'}

    print('Size of jobs:', len(result_dict['jobs']))

    try:
        """
        desc = getFullJobDesc(result_dict)
        if type(desc) != list:
            raise ValueError('Returned description is not of type list')
        i = 1
        for element in result_dict['jobs']:
            element['description'] = desc[i - 1]
            i += 1
        """
    except Exception as e:
        traceback.print_exc()
        return {"title": "Error Code 5: Couldn't retrieve full job descriptions"}

    return result_dict

# ---------------------------------------------------------------------------- #
@app.route('/search')
def search():

    keywords = request.args.get('keywords')
    location = request.args.get('location')
    pageNum = request.args.get('page')

    # CareerJet Jops
    careerjet_response = get_careerjet_jobs(keywords, location, pageNum)

    # Google Jobs
    if keywords:
        google_response = get_google_jobs(keywords, location, pageNum)
    else:
        google_response = {'status': 'Error: keyword(s) are required for google search'}

    jobs = {'careerjet jobs': careerjet_response, 'google jobs': google_response, 'total hits': 'TBD'}

    response = json.dumps(jobs, indent=4)

    return response

# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
	# setting debug to True enables hot reload
	# and also provides a debugger shell
	# if you hit an error while running the server
	app.run(debug = True)
