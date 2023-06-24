import requests

# Specify the API endpoint URL
url = "https://127.0.0.1:8001/authenticate"

# Optional: Define request headers if required by the API
headers = {}

# Optional: Define query parameters if required by the API
params = {}

# Path to the SSL certificate file
certificate_path = "/Users/notaris/git/raft/src/raft_node/ssl/certificate.crt"

# Define the username and password
username = "admin"
password = "admin"

# Create a tuple of username and password for Basic Authentication
auth_credentials = (username, password)

# Send the HTTPS request with SSL certificate verification and Basic Authentication
response = requests.get(url, headers=headers, params=params, verify=certificate_path, auth=auth_credentials)

# Process the response
if response.status_code == 200:  # Successful response
    data = response.json()  # Extract the JSON data from the response
    print(data)
else:
    print("Request failed with status code:", response.status_code)
    print(response.text)  # Print the response body for further inspection
