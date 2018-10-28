"""
TeamCity REST API Client
@Gidmaster
28 Oct 2018
"""

import requests

from urllib.parse import urljoin
import base64
import json
import getpass
import codecs
from os import getenv


def get_TC_credentials():
    username = getenv("TC_USERNAME", None)
    password = getenv("TC_PASSWORD", None)
    if username is None:
        username = input('Enter TC username: ')
    if password is None:
        password = getpass.getpass('Please enter TeamCity password for {}:'.format(username)).strip()
    return username, password

class RESTAPI_TeamCity:

    def __init__(self, username, password, server_name):
        """
        Class constructor
        """
        self.url = "https://{0}/app/rest/".format(server_name)
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (self.username, self.password) 
        self.session.mount(self.url, requests.adapters.HTTPAdapter(max_retries=3))       
        self.session.headers =  {
            "Accept": "application/json",
            'User-Agent': 'python-requests/2.18.4',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
            }
        try:
            self.session.get(self.url)
        except requests.exceptions.RequestException as e:
            print('Requests ERROR!')
            print(e)
            print('Url:', self.url)
        except Exception as e:
            print('ERROR!')
            print(e)
            print('Url:', self.url)        

    def __request_get(self, url_string,):
        """
        Do a custom query to teamcity server
        """
        url_full = urljoin(self.url, url_string)
        try:
            response = self.session.get(url_full)
            return response
        except requests.exceptions.RequestException as e:
            print('Requests ERROR!')
            print(e)
            print('Url:', url_full)
            return None
        except Exception as e:
            print('ERROR!')
            print(e)
            print('Url:', url_full)
            return None
        
    def get_projects(self):
        url_string = 'projects'
        return self.__request_get(url_string)

    def get_buildtypes(self):
        url_string = 'buildTypes'
        return self.__request_get(url_string)

    def get_builds_by_branch(self, buildtype_id, branch_name='<default>', count=10):
        url_string = f'builds/?locator=buildType:(id:{buildtype_id}),branch:name:{branch_name},count:{count}'
        return self.__request_get(url_string)

    def get_build_information_by_ID(self, buildID):
        url_string = f'buildTypes/id:{buildID}'
        return self.__request_get(url_string)

    def get_test_history_by_ID(self, testID):
        url_string = f'testOccurrences?locator=test:id:{testID}'
        return self.__request_get(url_string)

    def get_test_from_build(self, buildID):
        url_string = f'testOccurrences?locator=build:(id:{buildID}),count:500'
        return self.__request_get(url_string)

    def get_muted_tests_in_project(self, buildID):
        url_string = f'mutes/?locator=affectedProject:(buildType:(id:{buildID}))'
        response =  self.__request_get(url_string).json()['mute']

        return {mute['target']['tests']['test'][0]['name']: (mute['assignment']['text'] if 'text' in mute['assignment'].keys() else "No comment") for mute in response}
    
def main():
    username, password = get_TC_credentials()
    server = r'teamcity.dptechnology.com'

    client = RESTAPI_TeamCity(username, password, server)

    projects = client.get_projects()

    print(projects.json())


if __name__ == '__main__':
    main()