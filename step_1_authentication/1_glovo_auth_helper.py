#TODO is this file used?

import requests, config as config, os

payload = {
    "grantType": "client_credentials",
    "clientId": "175482686405285",
    "clientSecret": "dc190e6d0e4f4fc79e4021e4b981e596"
}
glovoUrl = config.API_URL;
# payload = {
#     "grantType": "client_credentials",
#     "clientId": os.getenv("API_KEY"),
#     "clientSecret": os.getenv("API_SECRET")
# }

headers = {"Content-Type": "application/json"}

response = requests.post(glovoUrl, json=payload, headers=headers)
print("Response", response);
print ("Status Code", response.status_code);

# Check request status
if response.status_code == 200:
    data = response.json()   # convert JSON response to dict
    print("Response Data:", data);
    #passing the value to the config file 
    config.Access_Token = data.get("accessToken") 

else:
    print("Error:", response.status_code, response.text)
