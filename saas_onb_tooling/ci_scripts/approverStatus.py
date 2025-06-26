import requests
import json
import os
import time

#Environment variables
projectId = os.environ['CI_PROJECT_ID']
mr_iid = os.environ['CI_MERGE_REQUEST_IID']
source_branch = os.environ['CI_MERGE_REQUEST_SOURCE_BRANCH_NAME']

#rh root cert for git api valiation
rh_cert_url = os.environ['rh_root']
os.system(f"curl {rh_cert_url} > /tmp/Current-IT-Root-CAs.pem")
rh_cert = '/tmp/Current-IT-Root-CAs.pem'  

# GitLab API settings
GITLAB_URL = os.environ['CI_SERVER_HOST']  
ACCESS_TOKEN = os.environ['git_api_token']  
# CODEOWNERS_PATH = "CODEOWNERS"
HEADERS = {
    "PRIVATE-TOKEN": ACCESS_TOKEN, 
    "Content-Type": "application/json"
    }

#Passing the projectID to the opened merge requests in the repository
def merge_open():
    url_mr = f"https://{GITLAB_URL}/api/v4/projects/{projectId}/merge_requests/{mr_iid}"
    # print(url_mr)

    # response_mr = Request(url_mr, headers=headers)
    response_mr = requests.get(url_mr, headers=HEADERS, verify=rh_cert)
    # getList_mr = urlopen(response_mr).read()
    # resp_mr = json.loads(getList_mr)
    resp_mr = json.loads(response_mr.content.decode('utf-8'))
    # print(resp_mr)
    merge_approval_check(projectId, mr_iid, resp_mr)

#function to check the approval status of the merge request
def merge_approval_check(x, y, z):
    projectId = x
    mr_iid = y
    url_approval = f"https://{GITLAB_URL}/api/v4/projects/{projectId}/merge_requests/{mr_iid}/approval_state"

    # response_approval = Request(url_approval, headers=headers)
    response_approval = requests.get(url_approval, headers=HEADERS, verify=rh_cert)
    # getList_approval = urlopen(response_approval).read()
    # resp_approval = json.loads(getList_approval)
    resp_approval = json.loads(response_approval.content.decode('utf-8'))
    # print(resp_approval)
    for i in resp_approval['rules']:
        # print(i['approvals_required'], len(i['approved_by']))
        if i['approved'] == True and i['rule_type'] == 'code_owner' and i['approvals_required'] <= len(i['approved_by']):
                # print(i['rule_type'])
                # if i['approvals_required'] <= len(i['approved_by']):
                        # print(len(i['approved_by']))
            # if i['approved'] == True :
            print('The Merge Request is now approved')
            
        else:
            print('Waiting for the Merge Request approval')
    #print('The Merge Request is now approved')
            print(time.ctime())
            time.sleep(60)
            merge_approval_check(x,y,z)

# if __name__ == "__main__":

merge_open()