import requests


class APIRequester:

    def __init__(self, _host, _port):
        self.host = _host
        self.port = _port
        self.url = f"https://{_host}:{_port}"

    def post_append_entry(self, payload_json, _endpoint="/append_entries"):
        send_url = self.url + _endpoint
        response = requests.post(send_url, data=payload_json, headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            return response.text
        else:
            return None
