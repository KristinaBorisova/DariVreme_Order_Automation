import requests, config as config, os

payload = {
    "grantType": "client_credentials",
    "clientId": "175482686405285",
    "clientSecret": "dc190e6d0e4f4fc79e4021e4b981e596"
}

# payload = {
#     "grantType": "client_credentials",
#     "clientId": os.getenv("API_KEY"),
#     "clientSecret": os.getenv("API_SECRET")
# }

headers = {"Content-Type": "application/json"}

response = requests.post(config.API_URL, json=payload, headers=headers)
print("Response", response);

# Check request status
if response.status_code == 200:
    data = response.json()   # convert JSON response to dict
    access_token = data.get("access_token")  # key name depends on API
    print("Bearer Token:", access_token)
else:
    print("Error:", response.status_code, response.text)
