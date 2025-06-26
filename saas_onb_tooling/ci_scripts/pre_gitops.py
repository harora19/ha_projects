import requests
import os
import shutil
import git

#rh root cert for git api valiation
rh_cert_url = os.environ['rh_root']
os.system(f"curl {rh_cert_url} > /tmp/Current-IT-Root-CAs.pem")
rh_cert = '/tmp/Current-IT-Root-CAs.pem'  
git_env=os.environ.copy()
git_env["GIT_SSL_CAINFO"]=rh_cert

# GitLab API settings
GITLAB_URL = os.environ['CI_SERVER_HOST']  # replace with gitlab env var
ACCESS_TOKEN = os.environ['git_api_token']  # replace with gitlab cicd var
GIT_NAMESPACE = os.environ['CI_PROJECT_NAMESPACE']
src_pre = os.environ['CI_PROJECT_DIR']
CODEOWNERS_PATH = "CODEOWNERS"
HEADERS = {
    "PRIVATE-TOKEN": ACCESS_TOKEN, 
    "Content-Type": "application/json"
    }

def check_folder_exists(folder_path, PROJECT_ID, BRANCH_NAME):
    parent_path = os.path.dirname(folder_path)
    folder_name = os.path.basename(folder_path)

    url = f"https://{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/tree"
    params = {
        "ref": BRANCH_NAME,
        "path": parent_path,
        "per_page": 100
    }

    response = requests.get(url, headers=HEADERS, params=params, verify=rh_cert)

    if response.status_code == 200:
        items = response.json()
        for item in items:
            if item["type"] == "tree" and item["name"] == folder_name:
                print(f"Folder already exists: {folder_path}")
                return True  # Exists
        print(f"Folder does not exist: {folder_path}")
        return False  # Does not exist
    else:
        print(f"API error for {folder_path}: {response.status_code}, {response.text}")
        return True  # Treat error as a fail

#Create a feature branch
def create_feature_branch(PROJECT_ID, FEATURE_BRANCH, MAIN_BRANCH):
    url = f"https://{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/branches"

    payload = {"branch": FEATURE_BRANCH, "ref": MAIN_BRANCH}
    
    response = requests.post(url, json=payload, headers=HEADERS, verify=rh_cert)
    
    if response.status_code == 201:
        print(f"Feature branch '{FEATURE_BRANCH}' created successfully.")
    elif response.status_code == 400 and "already exists" in response.text:
        print(f"Feature branch '{FEATURE_BRANCH}' already exists.")
    else:
        print(f"Failed to create feature branch: {response.status_code}, {response.text}")

#Create folders and commit changes
def create_folders(PROJECT_ID, FOLDERS, FEATURE_BRANCH):
    commit_url = f"https://{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/commits"
    
    actions = []
    
    # Create empty `.gitkeep` files to track folders
    for folder in FOLDERS:
        actions.append({
            "action": "create",
            "file_path": f"{folder}/.gitkeep",
            "content": "",
        })

    # Commit changes
    payload = {
        "branch": FEATURE_BRANCH,
        "commit_message": "Adding required folders",
        "actions": actions
    }

    response = requests.post(commit_url, json=payload, headers=HEADERS, verify=rh_cert)
    
    if response.status_code == 201:
        print("Folders created and committed successfully.")
    else:
        print(f"Failed to commit changes: {response.status_code}, {response.text}")

#Update Codeowners file
def update_codeowners(PROJECT_ID, new_codeowners_block, FEATURE_BRANCH, app_team_name):

    # Get the current content of CODEOWNERS
    get_url = f"https://{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/files/{CODEOWNERS_PATH.replace('/', '%2F')}/raw?ref={FEATURE_BRANCH}"

    response = requests.get(get_url, headers=HEADERS, verify=rh_cert)

    if response.status_code == 200:
        current_content = response.text
        updated_content = current_content.strip() + "\n" + new_codeowners_block.strip() + "\n"

        # Prepare payload for updating the file
        commit_url = f"https://{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/commits"
        payload = {
            "branch": FEATURE_BRANCH,
            "commit_message": f"Update CODEOWNERS file for {app_team_name}",
            "actions": [
                {
                    "action": "update",
                    "file_path": CODEOWNERS_PATH,
                    "content": updated_content
                }
            ]
        }

        # Update CODEOWNERS file
        commit_response = requests.post(commit_url, json=payload, headers=HEADERS, verify=rh_cert)

        if commit_response.status_code == 201:
            print(f"CODEOWNERS file updated successfully for team '{app_team_name}' in branch '{FEATURE_BRANCH}'.")
        else:
            print(f"Failed to update CODEOWNERS: {commit_response.status_code}, {commit_response.text}")
    else:
        print(f"Failed to fetch CODEOWNERS file: {response.status_code}, {response.text}")


#Create auto merge request 
def create_merge_request(PROJECT_ID, source_branch, target_branch, del_br, title):

    mr_url = f"https://{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/merge_requests"

    mr_payload = {
        "source_branch": source_branch,
        "target_branch": target_branch,
        "title": title,
        "description": "This MR adds the required folders and updates the CODEOWNERS file.",
        "remove_source_branch": del_br  # Set to True if you want to delete the feature branch after merge
    }
    mr_response = requests.post(mr_url, headers=HEADERS, json=mr_payload, verify=rh_cert)

    if mr_response.status_code == 201:
        print(f"Merge Request created: {title}")
    else:
        print(f"Failed to create MR: {mr_response.text}")

def tpl_push_trg(changed_files, trg_rep, BRANCH_NAME):

    trg_rep_cln_loc = f'/tmp/{trg_rep}'
    trg_rep_url = f"https://oauth2:{ACCESS_TOKEN}@{GITLAB_URL}/{GIT_NAMESPACE}/{trg_rep}.git"
    
    if os.path.exists(trg_rep_cln_loc):
        print(shutil.rmtree(trg_rep_cln_loc))
    else:
        print(f"no folder structure for target repo: {trg_rep} found ")

    print(f"Cloning Target Project {trg_rep}")
    repo_trg = git.Repo.clone_from(trg_rep_url, trg_rep_cln_loc, env=git_env)

    #Create a new branch in Project B
    # repo_trg.git.checkout('-b', BRANCH_NAME)
    if BRANCH_NAME in repo_trg.git.branch('-r'):
        print(f"Branch '{BRANCH_NAME}' already exists. Checking out the branch.")
        repo_trg.git.checkout(BRANCH_NAME)
    else:
        print(f"Creating and checking out new branch '{BRANCH_NAME}'.")
        repo_trg.git.checkout('-b', BRANCH_NAME)

    #Copy files from src Project to trg Project
    for file_rel_path in changed_files:
        src = os.path.join(src_pre, file_rel_path)
        dst = os.path.join(trg_rep_cln_loc, file_rel_path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"Copied {src} -> {dst} in the project {trg_rep}")

    #Commit & push changes in Project B
    repo_trg.git.add(all=True)
    commit_message = "Sync changed files from Source Project MR"
    repo_trg.index.commit(commit_message)
    # repo_trg.git.push('--set-upstream', 'origin', BRANCH_NAME)
    repo_trg.git.push('origin', BRANCH_NAME)
    print(f"Pushed changes to {BRANCH_NAME} in Target Project: {trg_rep}")
