import requests
import json
import os
from mr_gitops import extraxt_vars

# Set Vars
mr_data=extraxt_vars()
saas_API_TOKEN = os.environ['api_token'] #replace with gitlab cicd var
saas_BASE_URL = os.environ['saas_base_url']
saas_IAM_URL = os.environ['saas_iam_url']
stage_dep_role = 'Stage Operator'
prod_dep_role = 'Prod Author'
workspace_role = 'WORKSPACE_AUTHOR'

#Fetched from mr_gitops retun var
saas_work_name=mr_data.get("saas_workspace_name")
saas_team_name=mr_data.get("rover_group_name")

HEADERS = {
    "Authorization": f"Bearer {saas_API_TOKEN}",
    "Content-Type": "application/json"
}

def get_workspaces():
    """Fetch all workspaces and return their details."""
    url = f"{saas_BASE_URL}/workspaces"
    response = requests.get(url, headers=HEADERS)
    resp = json.loads(response.content.decode('utf-8'))
    return resp

def get_teams():
    """Fetch all teams and return their details."""
    url = f"{saas_IAM_URL}/teams"
    response = requests.get(url, headers=HEADERS)
    resp = json.loads(response.content.decode('utf-8'))
    return resp

def get_deployments():
    """Fetch all deployments and return their details."""
    url = f"{saas_BASE_URL}/deployments"
    payload = {}
    response = requests.request("GET", url, headers=HEADERS, data=payload)
    resp = json.loads(response.content.decode('utf-8'))
    # print(resp['deployments'])
    return resp

def update_workspace(workspace_id,stg_dep_id,stg_dep_name,prod_dep_id,prod_dep_name,team_id,team_name):
    payload={
        "organizationRole": "ORGANIZATION_MEMBER",
        "workspaceRoles": [
            {
            "role": workspace_role,
            "workspaceId": workspace_id
            }
        ],        
        "deploymentRoles": [
            {
                "role": stage_dep_role,
                "deploymentId": stg_dep_id
            },
            {
                "role": prod_dep_role,
                "deploymentId": prod_dep_id                
            }
        ]
    }
    response = requests.post(f"{saas_IAM_URL}/teams/{team_id}/roles", headers=HEADERS, json=payload)
    resp = json.loads(response.content.decode('utf-8'))
    # print(resp)
    # print(response.status_code)

    if response.status_code == 200:
        print(f"Team '{team_name}':'{team_id}' added to Deployment '{stg_dep_name}' '{stg_dep_id}' with role '{stage_dep_role}' and '{prod_dep_name}' '{prod_dep_id}' with role '{prod_dep_role}")
    elif response.status_code == 400:
        print(f"Bad Request: {response.text}")
    elif response.status_code == 404:
        print(f"Not Found: Check if the deployment or team ID is correct.")
    else:
        print(f"Error: {response.status_code} - {response.text}")

