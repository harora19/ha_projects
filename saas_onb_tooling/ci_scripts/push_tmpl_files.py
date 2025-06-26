import os
from mr_gitops import chk_chg_files
from pre_gitops import create_merge_request
from pre_gitops import tpl_push_trg

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

# repolist = {
#     'ddis' : '115886',
#     'onboarding' : '115904',
# }
MAIN_BRANCH = "main"  # The branch to create the feature branch from
FEATURE_BRANCH = os.environ['CI_MERGE_REQUEST_SOURCE_BRANCH_NAME']
STAGE_BRANCH = "stage"

template_files = []
chg_files=chk_chg_files()

for file_path in chg_files:

    if file_path.startswith("ci_checks/"):
        template_files.append(file_path)

    elif file_path.startswith("include/"):
        template_files.append(file_path)

    elif file_path.startswith("plugins/"):
        template_files.append(file_path)

    else:
        print(f"File not part of Templates, file is {file_path}")

if not template_files:
    print("No template files to push")
    exit(0)
else:
    print(f"Template files to push: {template_files}")
    
    for repo, repo_id in repolist.items():
        tpl_push_trg(template_files, repo, FEATURE_BRANCH)
        print(f"Template files pushed to {repo} with feature branch {FEATURE_BRANCH}")
        # MR1: Feature → Stage
        create_merge_request(repo_id, FEATURE_BRANCH, STAGE_BRANCH, False, f"Auto Merge {FEATURE_BRANCH} into {STAGE_BRANCH}")

        # MR2: Feature → Main
        create_merge_request(repo_id, FEATURE_BRANCH, MAIN_BRANCH, True, f"Auto Merge {FEATURE_BRANCH} into {MAIN_BRANCH}")