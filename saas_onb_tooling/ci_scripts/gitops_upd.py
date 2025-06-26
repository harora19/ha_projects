import os
from mr_gitops import extraxt_vars
from mr_gitops import chk_chg_files
from pre_gitops import create_feature_branch
from pre_gitops import create_folders
from pre_gitops import update_codeowners
from pre_gitops import create_merge_request
from pre_gitops import tpl_push_trg


# if __name__ == "__main__":
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

# repolist = {
#     'ddis' : '115886',
#     'onboarding' : '115904',
# }

mr_data=extraxt_vars()

app_team_name=mr_data.get("ddis_team_name").casefold()
astro_work_name=mr_data.get("astro_workspace_name").casefold()
astro_team_name=mr_data.get("rover_group_name")

PROJECT_ID = repolist[astro_work_name]

# List of folders to create
FOLDERS = [f'dags/{app_team_name}',f'plugins/{app_team_name}',f'include/{app_team_name}']

new_codeowners_block = f"""
[{app_team_name}] @Dataverse/astro/codeowners-groups/{astro_team_name}
/dags/{app_team_name}/
/plugins/{app_team_name}/
/include/{app_team_name}/
/tests/dags/
"""

MAIN_BRANCH = "main"  # The branch to create the feature branch from
# FEATURE_BRANCH = app_team_name+'-onb-to-'+astro_work_name
FEATURE_BRANCH = os.environ['CI_MERGE_REQUEST_SOURCE_BRANCH_NAME']
STAGE_BRANCH = "stage"

#Below are ONB changes
create_feature_branch(PROJECT_ID, FEATURE_BRANCH, MAIN_BRANCH)
create_folders(PROJECT_ID, FOLDERS, FEATURE_BRANCH)
update_codeowners(PROJECT_ID, new_codeowners_block, FEATURE_BRANCH, app_team_name)

#Below code will find changed files and will take appropriate actions
template_files = []
path_to_rover_chg = []
chg_files=chk_chg_files()

for file_path in chg_files:

    if file_path.endswith("add_rover_group.txt"):  
        path_to_rover_chg.append(file_path)
        tpl_push_trg(path_to_rover_chg, 'ddis', FEATURE_BRANCH)

        if astro_work_name != 'ddis':
            print("creating merge request in ddis repo containing add_rover_group.txt changes")
            #Stage merge request on ddis repo
            create_merge_request(repolist['ddis'], FEATURE_BRANCH, STAGE_BRANCH, False, f"Auto Merge {FEATURE_BRANCH} into {STAGE_BRANCH}")
            #Main merge request on ddis repo
            create_merge_request(repolist['ddis'], FEATURE_BRANCH, MAIN_BRANCH, True, f"Auto Merge {FEATURE_BRANCH} into {STAGE_BRANCH}")
 
    else:
        print(f"No changes made to add_rover_group or Templates folder, file is {file_path}")
# MR1: Feature → Stage
create_merge_request(PROJECT_ID, FEATURE_BRANCH, STAGE_BRANCH, False, f"Auto Merge {FEATURE_BRANCH} into {STAGE_BRANCH}")

# MR2: Feature → Main
create_merge_request(PROJECT_ID, FEATURE_BRANCH, MAIN_BRANCH, True, f"Auto Merge {FEATURE_BRANCH} into {MAIN_BRANCH}")