import requests
import json

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


def api_post_request(url, payload):
    # Convert the payload to JSON
    json_payload = json.dumps(payload)

    # Set the headers to specify that the content is JSON
    headers = {
        'Content-Type': 'application/json'
    }

    # Make the POST request
    response = requests.post(url, data=json_payload, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        # Request was successful
        # Return the JSON response
        return response.json()
    else:
        # Request was unsuccessful
        # Raise an exception with the error message
        raise Exception(f'Request failed with status code {response.status_code}')

