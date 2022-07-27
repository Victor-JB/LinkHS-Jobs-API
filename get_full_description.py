import ssl
import re
import traceback
from urllib.request import Request, urlopen
import requests
import json
from bs4 import BeautifulSoup, SoupStrainer
from concurrent.futures import ThreadPoolExecutor


def getFullJobDesc(jobsDict):
    descriptions = []
    urls = []
    try:
        jobsArr = jobsDict['jobs']
        for element in jobsArr:
            urls.append(str(element['url']))

        def get_url(url):
            return requests.get(url).text

        with ThreadPoolExecutor(max_workers=50) as pool:
            resList = list(pool.map(get_url, urls))

        for element in resList:
            soup = BeautifulSoup(element, 'html.parser')
            pageNumberArr = soup.find_all("script")[1]
            pageNumberArr = str(pageNumberArr).replace('<script type="application/ld+json">', "").replace("</script>",
                                                                                                          "")
            res = json.loads(pageNumberArr)
            res = res['description']
            res = res.split('<br>')
            for part in res:
                if part == ' ' or part == '':
                    res.remove(part)
            res = "".join(res)
            description = res.replace("<strong>", "").replace("</strong>", "").replace("<li>", "").replace("</li>",
                                                                                                           "").replace(
                "<ul>", "").replace("</ul>", "").replace("Posting Notes:", "")
            descriptions.append(description)
        return descriptions
        
    except Exception as err:
        traceback.print_exc()
        return " "
