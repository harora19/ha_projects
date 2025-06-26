import requests
import re
import os


# GitLab API vars
GITLAB_URL = os.environ['CI_SERVER_HOST'] 
ACCESS_TOKEN = os.environ['git_api_token'] 
PROJECT_ID = os.environ['CI_PROJECT_ID']
MERGE_REQUEST_ID = os.environ['CI_MERGE_REQUEST_IID']           
rh_cert_url = os.environ['rh_root']
os.system(f"curl {rh_cert_url} > /tmp/Current-IT-Root-CAs.pem")
rh_cert = '/tmp/Current-IT-Root-CAs.pem'            
headers = {"PRIVATE-TOKEN": ACCESS_TOKEN}

def extraxt_vars():

    url = f"https://{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_ID}"
    headers = {"PRIVATE-TOKEN": ACCESS_TOKEN}
    response = requests.get(url, headers=headers, verify=rh_cert)

    if response.status_code == 200:
        mr_data = response.json()
        description = mr_data.get("description", "")
        # print(description)
        
        # Parse key-value pairs using regex
        # pattern = r"(\w+):\s*([\w\-]+)"
        pattern = r"(\w+):'([^']+)'"
        parsed_data = dict(re.findall(pattern, description))
        return parsed_data 
        # print(parsed_data)

    else:
        print(f"Failed to fetch Merge Request: {response.status_code}, {response.text}")

#Below function checks and returns changed files (under templates or add_rover_group.txt)

def chk_chg_files():
    url=f"https://{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_ID}/changes"
    response = requests.get(url, headers=headers, verify=rh_cert)

    if response.status_code == 200:
        try:
            changes = response.json().get("changes", [])
            changed_files = [change["new_path"] for change in changes]
            print(changed_files)
            return changed_files            
            # print(changed_files)
        except requests.exceptions.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Raw response:\n{response.text}")