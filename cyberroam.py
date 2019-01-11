#!/usr/bin/env python3
import argparse
import xml.etree.ElementTree as ET
import json
import ssl
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BLOCK = 1024


class Config(object):
    '''
    Config can be used to set and get keys in the .cyberroam config
    file.
    '''

    def __init__(self, config_path='.cyberroam'):
        self.config_path = config_path

    def get(self, key):
        config_data = {}
        with open(self.config_path, 'r') as config:
            config_data = json.load(config)
        return config_data.get(key, None)

    def set(self, key, value):
        config_data = {}
        with open(self.config_path, 'r') as config:
            config_data = json.load(config)
        config_data[key] = value
        with open(self.config_path, 'w') as config:
            json.dump(config_data, config)


class Cyberroam(object):
    ''' The Cyberroam is capable of handling login and logout for Cyberroam
    captive portal. The username, password and mode of request must be
    provided in the '.cyberroam' config file or any other specified config
    path in a json format.
    '''

    # The captive portal provides a invalid ssl certificate and thus has been
    # made to skip certificate validation phase.

    context = ssl.SSLContext()
    context.verify_mode = ssl.CERT_NONE
    context.check_hostname = False

    def __init__(self, config_path='.cyberroam'):
        self.config = Config(config_path)

    def login(self, uri='/httpclient.html'):
        data = {
            'username': self.config.get('username'),
            'password': self.config.get('password'),
            'mode': self.config.get('login_mode'),
        }

        request = Request(
            self.config.get('host') + uri,
            data=urlencode(data).encode(),
        )
        response = urlopen(request, context=Cyberroam.context)

        response_data = ""
        while True:
            data = response.read(BLOCK)
            if not data:
                break
            response_data += data.decode()

        response_data = ET.fromstring(response_data)
        print(response_data.findtext('message'))  # Find something better.

    def logout(self, uri="/httpclient.html"):
        data = {
            'username': self.config.get('username'),
            'mode': self.config.get('logout_mode'),
        }

        request = Request(
            self.config.get('host') + uri,
            data=urlencode(data).encode(),
        )
        response = urlopen(request, context=Cyberroam.context)

        response_data = ""
        while True:
            data = response.read(BLOCK)
            if not data:
                break
            response_data += data.decode()

        response_data = ET.fromstring(response_data)
        print(response_data.findtext('message'))  # Find something better.


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    _parser_login = subparsers.add_parser('login', help='Cyberroam Login')
    _parser_logout = subparsers.add_parser('logout', help='Cyberroam Logout')

    argument_parser = parser.parse_args()
    if argument_parser.command == 'login':
        Cyberroam().login()
    elif argument_parser.command == 'logout':
        Cyberroam().logout()
    else:
        print('Command unknown')


if __name__ == '__main__':
    main()
