import requests
from mr_gitops import extraxt_vars
import os

mr_data=extraxt_vars()

# GitLab API vars
GITLAB_URL = os.environ['CI_SERVER_HOST'] 
ACCESS_TOKEN = os.environ['git_api_token'] 
PARENT_GROUP_ID = os.environ['saas_codeowners_group_id']   # Replace with the ID of the parent group which is the code-owner 
rh_cert_url = os.environ['rh_root']
os.system(f"curl {rh_cert_url} > /tmp/Current-IT-Root-CAs.pem")
rh_cert = '/tmp/Current-IT-Root-CAs.pem'  
SUBGROUP_NAME = mr_data.get("rover_group_name")  #Fetched from mr_gitops retun var
SUBGROUP_PATH = mr_data.get("rover_group_name")  #Fetched from mr_gitops retun var
ACCESS_LEVEL = 30  
LDAP_CN = mr_data.get("rover_group_name")
LDAP_PROVIDER = "ldapmain"  
saas_work_name=mr_data.get("saas_workspace_name")
headers = {"PRIVATE-TOKEN": ACCESS_TOKEN}

#Workspace project ids
repolist = {
    'ddis' : '123425',
    'marketing' : '543323',
    'finance' : '653423',
    'domain-independent' : '876656',
    'sales' : '112233',
    'engineering' : '323211',
    'operations' : '545668',
    'people' : '000221'
}

def create_subgroup():

    create_subgroup_url = f"https://{GITLAB_URL}/api/v4/groups"

    subgroup_payload = {
        "name": SUBGROUP_NAME,
        "path": SUBGROUP_PATH,
        "parent_id": PARENT_GROUP_ID,
        "visibility": "internal"  
    }

    response = requests.post(create_subgroup_url, json=subgroup_payload, headers=headers, verify=rh_cert)
    # print(response)

    if response.status_code == 201:
        subgroup_id = response.json()["id"]
        print(f"Subgroup '{SUBGROUP_NAME}' created successfully with ID {subgroup_id}.")
        return subgroup_id

    else:
        print(f"Failed to create subgroup: {response.status_code}, {response.text}")


def map_ldap(sub_id):
    
    ldap_url = f"https://{GITLAB_URL}/api/v4/groups/{sub_id}/ldap_group_links"

    ldap_payload = {
        "cn": LDAP_CN, 
        "group_access": 30,  
        "provider": LDAP_PROVIDER
    }
    ldap_response = requests.post(ldap_url, json=ldap_payload, headers=headers, verify=rh_cert)

    if ldap_response.status_code == 201:
        print(f"LDAP group '{LDAP_CN}' added successfully to subgroup.")
    else:
        print(f"Failed to add LDAP group: {ldap_response.status_code}, {ldap_response.text}")

def invite_group(sub_id):
    for app in repolist:
        # if app == saas_work_name:
        if app.casefold() == saas_work_name.casefold():

            url = f"https://{GITLAB_URL}/api/v4/projects/{repolist[app]}/share"

            
            payload = {
                "group_id": sub_id,
                "group_access": ACCESS_LEVEL,  
                "expires_at": None  
            }

            # Headers
            headers = {
                "PRIVATE-TOKEN": ACCESS_TOKEN,
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers, verify=rh_cert)

            if response.status_code == 201:
                print(f"Group {SUBGROUP_NAME} successfully invited to project {app}:{repolist[app]} with access level {ACCESS_LEVEL}.")
            else:
                print(f"Failed to invite group: {response.status_code}, {response.text}")



if __name__ == "__main__":
    sub_id=create_subgroup()
    map_ldap(sub_id)
    invite_group(sub_id)

# Exception handling can be implemented in create_subgroup() Response code 400 "has already been taken\" can be handled by adding integer in the suffix