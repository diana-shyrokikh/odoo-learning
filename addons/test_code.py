import requests
import json

url = "http://localhost:8071/web/webclient/version_info"

payload = json.dumps({})

headers = {
    "Content-Type": "application/json",
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
