import requests
import json
import os
from mr_gitops import extraxt_vars
from saas_onboarding import get_deployments
from saas_onboarding import get_teams
from saas_onboarding import get_workspaces
from saas_onboarding import update_workspace

# Set Vars
mr_data=extraxt_vars()
saas_API_TOKEN = os.environ['api_token'] #replace with gitlab cicd var
saas_IAM_URL = os.environ['saas_iam_url']
saas_work_name=mr_data.get("saas_workspace_name")
saas_team_name=mr_data.get("rover_group_name")
# print(saas_team_name)

if __name__ == "__main__":
    all_works = get_workspaces()['workspaces']
    dep_data=get_deployments()['deployments']
    team_data=get_teams()['teams']
    # print(team_data['name'])

    for x in dep_data:
        if x['workspaceName'] == saas_work_name and x['name'].endswith("-stage"):
            stage_dep_id = x['id']
            stage_dep_name = x['name']  
        elif x['workspaceName'] == saas_work_name and x['name'].endswith("-prod"):
            prod_dep_id = x['id']
            prod_dep_name = x['name']              

    print(f'stage deployment name and id: {stage_dep_name} {stage_dep_id}')
    print(f'prod deployment name and id: {prod_dep_name} {prod_dep_id}')

    for y in team_data:
        if y['name'] == saas_team_name:
            team_id = y['id']
            team_name = y['name']
    
    for z in all_works:
        if z['name'] == saas_work_name:
            workspace_id = z['id']
            workspace_name = z['name']
    
    print(f'required team name and id: {team_name} {team_id}')
    print(f'required workspace name and workspaceid: {workspace_name} {workspace_id}')

# def update_workspace(workspace_id,stg_dep_id,stg_dep_name,prod_dep_id,prod_dep_name,team_id)
    update_workspace(workspace_id,stage_dep_id,stage_dep_name,prod_dep_id,prod_dep_name,team_id,team_name)