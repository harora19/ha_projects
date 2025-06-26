# SaaS Onboarding Automation

This project automates the onboarding of user groups into a SaaS-based tool and the associated GitLab repository that is mapped to the SaaS tool. The automation is orchestrated using a GitLab CI/CD pipeline with multiple stages, each responsible for a specific part of the onboarding process.

## Pipeline Stages

### 1. validate_team_exists

- **Purpose:** Checks whether the target team already exists in the SaaS tool.
- **Behavior:**  
  - If the team exists, the CI pipeline stops and prints a message indicating that the team already exists.
  - If the team does not exist, the pipeline continues to the next stage.

### 2. git_approver_status

- **Purpose:** Waits for the appropriate approver to approve the merge request.
- **Behavior:**  
  - The pipeline pauses until the required code owner or approver has approved the merge request.

### 3. saas_gitops

- **Purpose:** Performs Git operations to set up access and code ownership in the GitLab repository.
- **Behavior:**  
  - Creates a subgroup in GitLab to enable CODEOWNERS functionality.
  - Maps an LDAP group to the newly created subgroup.
  - Invites this group to the repository where the SaaS tool's code resides.

#### Parallel Stage: gitops_prefix_codeowner

- **Purpose:** Sets up folder structure and code ownership in the SaaS repository.
- **Behavior:**  
  - Creates required prefixes or folders in the SaaS repository.
  - Modifies the `CODEOWNERS` file to reflect new ownership.
  - Creates merge requests for these changes using the GitLab API.

### 4. saas_work_onb

- **Purpose:** Onboards the new team into the SaaS tool using its API.
- **Behavior:**  
  - Assigns the team the desired access or role within the SaaS tool.

### 5. push_tmpl_files

- **Purpose:** Pushes essential template files or scripts to the SaaS repository.
- **Behavior:**  
  - Ensures that required templates or scripts are available for operations in the SaaS repository.

---

## Summary

This automation streamlines the process of onboarding new teams by integrating SaaS tool access, GitLab repository setup, code ownership management, and deployment of essential templates, all managed through a robust CI/CD pipeline.