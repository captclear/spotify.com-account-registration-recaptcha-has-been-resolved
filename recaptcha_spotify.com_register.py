from math import fabs
import requests
import json
import uuid
import random
import string
import re


# captcha api config on https://www.clearcaptcha.com 
clearcaptcha_recaptcha_api="http://api.clearcaptcha.com/captcha/recaptcha_enterprise_v2v3";
token = 'test'
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


def generate_random_string(length):
    letters = string.ascii_letters 
    return ''.join(random.choice(letters) for _ in range(length))

session = requests.Session()

headers={
        "User-Agent": user_agent,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.spotify.com/",
        "Origin": "https://www.spotify.com",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Connection": "keep-alive",
    }

response = session.get("https://www.spotify.com/us/signup?forward_url=https%3A%2F%2Fopen.spotify.com%2F",headers=headers,verify=False)
response_data=response.text
api_key=re.search(r'"signupServiceAppKey"\s*:\s*"([^"]+)"', response_data).group(1)
installation_id=re.search(r'"spT"\s*:\s*"([^"]+)"', response_data).group(1)
flow_id=re.search(r'"flowId"\s*:\s*"([^"]+)"', response_data).group(1)

post_data =  {
    "token": token,
    "sitekey": "6LfCVLAUAAAAALFwwRnnCJ12DalriUGbj8FW_J39",
    "referer":"https://www.spotify.com/",
    "recaptcha_anchor_size":"invisible",
    "page_title":"Sign up - Spotify",
    "action":"website/signup/submit_email"
}
response = requests.post(clearcaptcha_recaptcha_api, data=post_data)
response_data = response.json()
recaptcha_token=response_data.get("data", {}).get("recaptcha_token", {})


random_email = generate_random_string(12)+"@gmail.com"
post_data =  {
		"account_details": {
		"birthdate": "1999-02-12",
		"consent_flags": {
			"eula_agreed": True,
			"send_email": True,
			"third_party_email": True
		},
		"display_name": "wasdfas",
		"email_and_password_identifier": {
			"email": random_email,
			"password": "sfdasfda.123"
		},
		"gender": 5
	},
	"callback_uri": "https://www.spotify.com/signup/challenge?flow_ctx="+flow_id+"%3A1725101559&locale=us",
	"client_info": {
		"api_key": api_key,
		"app_version": "v2",
		"capabilities": [
			1
		],
		"installation_id": installation_id,
		"platform": "www"
	},
	"tracking": {
		"creation_flow": "",
		"creation_point": "https://www.spotify.com/us/signup",
		"referrer": ""
	},
	"recaptcha_token": recaptcha_token,
	"submission_id": "97543ddf-9c22-4600-b8d3-43027805f8a5",
	"flow_id": flow_id
}
post_data=json.dumps(post_data)

headers["Content-Type"]="application/json"
response = session.post("https://spclient.wg.spotify.com/signup/public/v2/account/create", data=post_data,headers=headers,verify=False)
if response.status_code == 200:
    response_data = response.json()
    print(response_data)
    session_id=response_data["challenge"]["session_id"]
    
    post_data =  {
        "session_id": session_id
    }
    post_data=json.dumps(post_data)
    
    response = session.post("https://challenge.spotify.com/api/v1/get-session", data=post_data,headers=headers,verify=False)
    response_data = response.json()
    challenge_id=response_data["in_progress"]["challenge_details"]["challenge_id"]
    
    post_data =  {
        "token": token,
        "sitekey": "6LeO36obAAAAALSBZrY6RYM1hcAY7RLvpDDcJLy3",
        "referer":"https://challenge.spotify.com/",
        "recaptcha_anchor_size":"normal",
        "page_title":"Spotify",
        "sa":"challenge"
    }
    response = requests.post(clearcaptcha_recaptcha_api, data=post_data)
    response_data = response.json()
    recaptcha_token=response_data.get("data", {}).get("recaptcha_token", {})
    
    post_data =  {
	    "session_id": session_id,
	    "challenge_id": challenge_id,
	    "recaptcha_challenge_v1": {
		    "solve": {
			    "recaptcha_token": recaptcha_token
		    }
	    }
    }
    post_data=json.dumps(post_data)
    response = session.post("https://challenge.spotify.com/api/v1/invoke-challenge-command", data=post_data,headers=headers,verify=False)
    print(response.text)
    
    post_data =  {
	    "session_id": session_id
    }
    post_data=json.dumps(post_data)
    response = session.post("https://spclient.wg.spotify.com/signup/public/v2/account/complete-creation", data=post_data,headers=headers,verify=False)
    if "login_token" in response.text:
        print(response.json());
    else:
        response_data={
            "error": "complete-creation error",
            "status_code": response.status_code,
            "response": response.text
        }
        print(response_data)

    
else:
    response_data={
        "error": "api error",
        "status_code": response.status_code,
        "response": response.text
    }
    print(response_data)
    



