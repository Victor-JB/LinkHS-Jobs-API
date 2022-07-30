
import requests
from bs4 import BeautifulSoup
import pandas as pd

# ---------------------------------------------------------------------------- #
def get_url(search_terms = '', location = ''):

    # separate words in search/location
    search_list = search_terms.split()
    location_list = location.split()

    # join lists to create pieces of url
    base_url = "https://www.indeed.com/jobs?"
    query_url = "q=" + '%20'.join(search_list)
    location_url = '&l=' + '%20'.join(location_list)

    # combine pieces to create full url
    return base_url + query_url + location_url

# ---------------------------------------------------------------------------- #
def main():
    search_terms = "high school part time"
    location = "San Francisco"

    # load indeed search results
    url = get_url(search_terms, location)

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15'}
    response = requests.get(url, headers=headers)
    print(response.text)
    soup = BeautifulSoup(response.content, "html.parser")

    # get jobs from first page of results (~15 jobs)
    jobs = soup.find_all('td', class_ = "resultContent")
    print("jobs:", jobs)

    # get urls for full job listing details
    urls = []
    for job in jobs:
        url = job.find('a').get("href")
        urls.append("https://www.indeed.com" + url)

    titles = []
    companies = []
    descriptions = []
    for url in urls:

        # load url for each job listing
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        # get job title & job description
        title = soup.find('h1')
        company = soup.find('div', class_ = "icl-u-lg-mr--sm icl-u-xs-mr--xs")
        description = soup.find('div', id = "jobDescriptionText")

        # add to list
        if None not in [title, company, description]:
            titles.append(title.text)
            companies.append(company.text)
            descriptions.append(description.text)

    # create df from results
    jobs_df = pd.DataFrame({
        'title': titles,
        'company_name': companies,
        'description': descriptions
    })

    # write to csv
    jobs_df.to_csv("indeed_jobs.csv")

# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()
