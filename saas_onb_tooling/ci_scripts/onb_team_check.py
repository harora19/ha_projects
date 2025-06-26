from mr_gitops import extraxt_vars
from pre_gitops import check_folder_exists
import sys

mr_data=extraxt_vars()
app_team_name=mr_data.get("ddis_team_name").casefold()
saas_work_name=mr_data.get("saas_workspace_name").casefold()

FOLDER_PATH = [f'dags/{app_team_name}',f'plugins/{app_team_name}',f'include/{app_team_name}']

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

PROJECT_ID = repolist[saas_work_name]

MAIN_BRANCH = "main"
STAGE_BRANCH = "stage"


def check_team_exists(br_name):
    chk_pref = []
    for path in FOLDER_PATH:
        if check_folder_exists(path, PROJECT_ID, br_name):
            chk_pref.append(path)

    # Final decision
    if chk_pref:
        print(f"\n Error: Input Team {app_team_name} already exist in the repo:{saas_work_name}, because the following folders already exist:")
        for f in chk_pref:
            print(f" - {f} in {br_name}")
        sys.exit(1)
    else:
        print(f"\nAll folders are new with unique names unavailable in branch {br_name} safe to create!")

if __name__ == "__main__":
#Check whether input team name already exists in Stage Branch in the target saas Repo
    check_team_exists(STAGE_BRANCH)
#Check whether input team name already exists in Main Branch in the target saas Repo
    check_team_exists(MAIN_BRANCH)
