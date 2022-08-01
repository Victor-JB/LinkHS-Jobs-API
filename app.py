
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

# limiting the number of pages to fetch
import time

import traceback
from get_full_description import getFullJobDesc

app = Flask(__name__)

# ---------------------------------------------------------------------------- #
def get_google_jobs(keywords, location, pageNum, FETCH_ALL_JOBS):

    if not FETCH_ALL_JOBS:
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

    try:
        # connect to Google Jobs API
        client = GoogleSearch(params)
        results = client.get_dict()

    except Exception as e:
        traceback.print_exc()
        return {'error': f'Error Code 2: API query failed. Failed to retrieve jobs from Google Jobs API with info: loc={location}, keywords={keywords}, pageNum={pageNum}'}

    if 'error' in results:
        return results

    if results['search_metadata']['status'] != 'Success':
        results = 'Search failed'
    else:
        del results['search_metadata']

    if FETCH_ALL_JOBS:

        pageTimer = time.time()
        currentPage = 0
        print(f"\nSearching for '{keywords}' in '{location}' until time is up")

        while (time.time()-pageTimer) < 10:
            currentPage += 1
            next_result = get_google_jobs(keywords, location, currentPage, False)
            if 'error' not in next_result:
                results['jobs_results'].extend(next_result['jobs_results'])

        del results['search_parameters']

    return results

# ---------------------------------------------------------------------------- #
def get_careerjet_jobs(keywords, location, pageNum, FETCH_ALL_JOBS):

    try:
        # initializing the CareerJet client
        cj = CareerjetAPIClient("en_US")

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
                'page': str(pageNum),
            })

    except Exception as e:
        traceback.print_exc()
        return {'error': f'Error Code 2: API query failed. Failed to retrieve jobs from CareerJet API with info: loc={location}, keywords={keywords}, pageNum={pageNum}'}


    # testing
    if type(result_dict) is dict:
        if result_dict['type'] == 'LOCATIONS':
            return {'error': "Error Code 4: CareerJet response type is not 'JOBS'"}
        if result_dict['hits'] == 0:
            return {"error": "Error Code 1 (No Jobs Available)"}
    else:
        return {'error': f'Error Code 3: CareerJet API response did not pass testing. Response: {result_dict}'}

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
        return {"error": "Error Code 5: Couldn't retrieve full job descriptions"}

    if FETCH_ALL_JOBS:

        pageTimer = time.time()
        numPages = int(result_dict['pages'])
        print(f"\nNumber of pages to search for '{keywords}' in '{location}': {numPages}")

        currentPage = 1
        numPagesRemaining = numPages - 1
        while numPagesRemaining != 0 and (time.time()-pageTimer) < 10:
            currentPage += 1
            next_result = get_careerjet_jobs(keywords, location, currentPage, False)
            result_dict['jobs'].extend(next_result['jobs'])
            numPagesRemaining -= 1

    return result_dict

# ---------------------------------------------------------------------------- #
@app.route('/search')
def search():

    keywords = request.args.get('keywords')
    location = request.args.get('location')
    pageNum = request.args.get('page')
    FETCH_ALL_JOBS = False

    start = time.time()
    if not pageNum:
        print("No page number specified; fetching all jobs...")
        FETCH_ALL_JOBS = True

    # CareerJet Jobs
    careerjet_response = get_careerjet_jobs(keywords, location, pageNum, FETCH_ALL_JOBS)
    if 'error' not in careerjet_response:
        num_careerjet_jobs = len(careerjet_response['jobs'])
        print("Num Careerjet jobs:", num_careerjet_jobs)

    else:
        num_careerjet_jobs = 0

    # Google Jobs
    if keywords:
        google_response = get_google_jobs(keywords, location, pageNum, FETCH_ALL_JOBS)

        if 'error' not in google_response:
            num_google_jobs = len(google_response['jobs_results'])
            print("Num Google jobs:", num_google_jobs)

            total_jobs = num_careerjet_jobs + num_google_jobs

        else:
            total_jobs = num_careerjet_jobs
    else:
        google_response = {'status': 'Error: keyword(s) are required for google search'}
        total_jobs = num_careerjet_jobs

    print("\nTotal jobs:", total_jobs)
    jobs = {'careerjet jobs': careerjet_response, 'google jobs': google_response, 'total hits': f'{total_jobs}'}

    response = json.dumps(jobs, indent=4)

    print("\nTotal time:", time.time() - start)
    return response

# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
	# setting debug to True enables hot reload
	# and also provides a debugger shell
	# if you hit an error while running the server
	app.run(debug = True)
