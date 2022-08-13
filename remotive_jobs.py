
"""
Description: Test the Remotive API
Author: Victor J.
Date: 8/13/2022
"""

# fetching the jobs
import requests

# converting to dictionary
import json

# limiting the number of pages to fetch
import time

BASE_URL = 'https://remotive.com/api/remote-jobs?search='

# ---------------------------------------------------------------------------- #
def getRemotiveJobs(search_terms):
    start = time.time()

    url = BASE_URL + str(search_terms)

    response = requests.get(url)

    if response.status_code != 200:
        return {'error': f'Recieved status code {response.status_code} for remotive jobs with error {response.text}'}
    else:
        response_json = json.loads(response.text)

    print("\nFinished fetching Remotive jobs in", time.time() - start)
    return response_json

# ---------------------------------------------------------------------------- #
if __name__ == "__main__":

    search_terms = "front end"
    jobs_json = getRemotiveJobs(search_terms)

    print(jobs_json)
