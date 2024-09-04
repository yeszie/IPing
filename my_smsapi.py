from smsapi.client import SmsApiPlClient
import requests

def send_sms(api_token, to, message, from_=""):
    url = "https://api.smsapi.pl/sms.do"
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    data = {
        "to": to,
        "message": message,
        "from": from_
    }

    response = requests.post(url, headers=headers, data=data)
    
    try:
        response_data = response.json()
    except ValueError:
        response_data = response.text
    
    return response_data


api_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
to = "4800000000"
message = "test sms"
from_ = "IPing.pl"

response = send_sms(api_token, to, message, from_)
print(response)
