
'''
    Purpose: Simple script to set up API access for a user
    Description: Send a few POST requests to the API to set up your user credentials
    in order to have access to the API
    Background: In order to gain access to the API, the API first needs to have you
    registered. In order to do that, you must send a requests to /signup, which
    will register your form data (see below) in the database. Then, you must login
    by visiting /login and sending a request with a form containing your email and
    password. You will be returned a JWT toke—make sure to record that somewhere!
    That will be your access token to the API. Then, you can actually use the API
    at /search in order to query the API itself—make sure to use that JWT token
    you were given in your request!

    Let me know if you have any questions :)
'''

# The only library we'll need is requests
import requests

# jk :)
import os

BASE_URL = 'http://127.0.0.1:5000/'
# BASE_URL = 'https://linkhs-job-api.herokuapp.com/'

# ---------------------------------------------------------------------------- #
def register(name, email, password):

    url = BASE_URL + 'signup'
    params = {'name': name, 'email': email, 'password': password}
    print(f'\nSending request to {url} with form data {params} ...')
    try:
        r_register = requests.post(url, data=params)
        return r_register
    except Exception as e:
        print(e)

# ---------------------------------------------------------------------------- #
def login(email, password):

    url = BASE_URL + 'login'
    params = {'email': email, 'password': password}
    print(f'\nSending request to {url} with form data {params} ...')
    try:
        r_login = requests.post(url, data=params)
        return r_login
    except Exception as e:
        print(e)

# ---------------------------------------------------------------------------- #
def test_API(token):

    url = BASE_URL + 'search?keywords=dog&location=california&page=2'
    params = {'x-access-token': token}
    print(f'\nSending request to {url} with form data {params} ...')
    try:
        res = requests.post(url, data=params)
        return res
    except Exception as e:
        print(e)

# ---------------------------------------------------------------------------- #
def main():
    name = input('Enter your name: ')
    email = input('Enter your email: ')
    password = input('Enter the password you will use to login: ')

    r_register = register(name, email, password)
    if r_register.status_code == 201:
        print('Success! Your credentials have been logged')
    else:
        raise Exception(f'\nUh oh! Request errd with code {r_register.status_code} and message {r_register.json()}')

    r_login = login(email, password)
    if r_login.status_code == 201:
        print('Success! You are now logged in!')
    else:
        raise Exception(f'\nUh oh! Request errd with code {r_login.status_code} and message {r_login.json()}')

    token_json = r_login.json()
    print(f'\n{token_json}\nThe JSON above contains your unique login token')
    print('Be sure not to lose it, as you will use the token for every call to the API')

    with open(".env", "a+") as f:
        f.write(f"JOBS_API_KEY='{token_json['token']}'")

    print('\nAn env file has been auto-appended/created with the credentials')

    print('\nIn order to test your token, we will use it to request the API')
    response = test_API(token_json['token'])
    try:
        response_json = response.json()
        print("Success! You're all set")
        print(f'Here are the jobs:', response_json)

    except Exception as e:
        print('Uh oh!')

if __name__ == '__main__':
    main()
