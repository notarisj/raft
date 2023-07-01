import requests
import json

from requests import RequestException
from requests.auth import HTTPBasicAuth

from src.configuration_reader import IniConfig

"""
    Example usage

    payload = {
        'key1': 'value1',
        'key2': 'value2'
    }

    url = 'https://api.example.com/data'

    try:
        response = make_api_post_request(url, payload)
        print(response)
    except Exception as e:
        print('Error:', str(e))
"""

raft_config = IniConfig('src/configurations/config.ini')


def get_server_state(host, port, username, password):
    """
    Get the state of a server

    Args:
        host (str): Hostname of the server
        port (str): Port of the server
        username (str): Username for the API
        password (str): Password for the API

    Returns:
        dict: JSON response from the API server

    Raises:
        RequestException: If the request to the API server fails
        ValueError: If the JSON response from the API server is invalid
    """
    url = f'https://{host}:{port}/get_state'
    try:
        response = api_get_request(url, username, password)
        if response is None:
            return {'status': 'ERROR', 'message': 'Could not connect to API server.'}
        elif response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            return {'status': 'ERROR', 'message': 'Login failed, incorrect username or password.'}
    except RequestException:
        return {'status': 'ERROR', 'message': 'Request to API server failed.'}
    except ValueError:
        return {'status': 'ERROR', 'message': 'Invalid JSON response from API server.'}


class ApiHelper:

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def login(self):
        """
        Login to the API server
        """
        response = self.make_api_get_request('authenticate')
        if response is None:
            return {'login': False, 'message': 'Error: Could not connect to API server'}
        elif response.status_code == 200:
            return {'login': True, 'message': 'Login successful'}
        elif response.status_code == 401:
            return {'login': False, 'message': 'Login failed: Incorrect username or password'}

    def get_servers(self):
        response = self.make_api_get_request('get_servers')
        if response is None:
            return {'get_state': False, 'message': 'Error: Could not connect to API server'}
        elif response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            return {'get_state': False, 'message': 'Login failed: Incorrect username or password'}

    def start_stop_server(self, host, port, action, username=None, password=None):
        if username is None or password is None:
            username = self.username
            password = self.password
        url = f'https://{host}:{port}/{action}'
        try:
            return api_post_request(url, {}, username, password)
        except Exception as e:
            print('Error:', str(e))

    def node_actions(self, host, port, payload, action, username=None, password=None):
        """
        Perform an action on a node add_node, update_node, delete_node

        Args:
            host (str): Hostname of the server
            port (str): Port of the server
            payload (dict): Payload to send to the API server
            action (str): Action to perform on the node
            username (str): Username for the API (optional)
            password (str): Password for the API (optional)

        Returns:
            bool: True if the request was successful, False otherwise

        Raises:
            Exception: If the request to the API server fails
        """
        if username is None or password is None:
            username = self.username
            password = self.password
        if action == 'delete_node':
            url = f'https://{host}:{port}/{action}/{payload}'
            payload = {}
        else:
            url = f'https://{host}:{port}/{action}'
        try:
            response = api_post_request(url, payload, username, password)
            if response is None:
                return False
            elif response.status_code == 200:
                return True
        except Exception as e:
            print('Error:', str(e))

    def make_api_post_request(self, endpoint, payload):
        """
        Wrapper for the api_post_request function to make a
        POST request to the API server without having to specify
        the username and password every time

        Args:
            endpoint (str): Endpoint to send the request to
            payload (dict): Payload to send to the API server

        Returns:
            dict: JSON response from the API server

        Raises:
            Exception: If the request to the API server fails
        """
        url = f'https://{self.host}:{self.port}/{endpoint}'
        try:
            return api_post_request(url, payload, self.username, self.password)
        except Exception as e:
            print('Error:', str(e))

    def make_api_get_request(self, endpoint):
        """
        Wrapper for the api_get_request function to make a
        GET request to the API server without having to specify
        the username and password every time

        Args:
            endpoint (str): Endpoint to send the request to

        Returns:
            dict: JSON response from the API server

        Raises:
            Exception: If the request to the API server fails
        """
        url = f'https://{self.host}:{self.port}/{endpoint}'
        try:
            return api_get_request(url, self.username, self.password)
        except Exception as e:
            print('Error:', str(e))


def api_post_request(url, payload, username='admin', password='admin'):
    """
    Make a POST request to the API server

    Args:
        url (str): URL to send the request to
        payload (dict): Payload to send to the API server
        username (str): Username for the API
        password (str): Password for the API

    Returns:
        requests.Response: Response from the API server

    Raises:
        Exception: If the request to the API server fails
    """
    # Convert the payload to JSON
    json_payload = json.dumps(payload)

    # Set the headers to specify that the content is JSON and include basic authentication credentials
    headers = {
        'Content-Type': 'application/json'
    }

    # Make the POST request with basic authentication
    response = requests.post(url, data=json_payload, headers=headers, auth=HTTPBasicAuth(username, password),
                             verify=raft_config.get_property('SSL', 'ssl_cert_file'))

    # Check the response status code
    if response.status_code == 200:
        # Request was successful
        # Return the JSON response
        return response
    else:
        # Request was unsuccessful
        # Raise an exception with the error message
        raise Exception(f'Request failed with status code {response.status_code}')


def api_get_request(url, username='admin', password='admin'):
    """
    Make a GET request to the API server

    Args:
        url (str): URL to send the request to
        username (str): Username for the API
        password (str): Password for the API

    Returns:
        requests.Response: Response from the API server
    """
    # Set the headers to include basic authentication credentials
    headers = {}

    # Make the GET request with basic authentication
    response = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, password),
                            verify=raft_config.get_property('SSL', 'ssl_cert_file'))

    # Check the response status code
    return response
