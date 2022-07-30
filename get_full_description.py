import ssl
import re
import traceback
from urllib.request import Request, urlopen
import requests
import json
from careerjet_api import CareerjetAPIClient
from bs4 import BeautifulSoup, SoupStrainer
from concurrent.futures import ThreadPoolExecutor

# ---------------------------------------------------------------------------- #
def getFullJobDesc(jobsDict):
    descriptions = []
    urls = []
    try:
        jobsArr = jobsDict['jobs']

        for element in jobsArr:
            urls.append(str(element['url']))

        print("\nUrls:", urls[0:4])

        def get_url(url):
            return requests.get(url).text

        with ThreadPoolExecutor(max_workers=50) as pool:
            resList = list(pool.map(get_url, urls))
            print("Threads done")

        for element in resList:
            soup = BeautifulSoup(element, 'html.parser')
            print(soup.prettify())
            pageNumberArr = soup.find_all("script")[1]
            pageNumberArr = str(pageNumberArr).replace('<script type="application/ld+json">', "").replace("</script>",
                                                                                                          "")
            res = json.loads(pageNumberArr)['description']
            res = res.split('<br>')
            print("\nInitial parsing finished")
            for part in res:
                if part == ' ' or part == '':
                    res.remove(part)

            res = "".join(res)
            description = res.replace("<strong>", "").replace("</strong>", "").replace("<li>", "").replace("</li>",
                                                                                                           "").replace(
                "<ul>", "").replace("</ul>", "").replace("Posting Notes:", "")
            print("\nDescription is cleaned")
            descriptions.append(description)
        return descriptions

    except Exception as err:
        traceback.print_exc()
        return " "

# ---------------------------------------------------------------------------- #
if __name__ == "__main__":

    try:
        cj = CareerjetAPIClient("en_US")
        location = 'san francisco'
        keywords = 'data scientist'
        pageNum = '0'

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

    except Exception as e:
        print(f'API query failed\nFailed to retrieve jobs from CareerJet API with info: loc={location}, keywords={keywords}, pageNum={pageNum}')
        print(f'Error:\n{e}')

    if len(result_json['jobs']) != 99 or type(result_json) is not dict:
        raise Exception('CareerJet API response did not pass testing. Response:', result_json)

    print('Size of jobs:', len(result_json['jobs']))

    descriptions = getFullJobDesc(result_json)

    print(descriptions)
