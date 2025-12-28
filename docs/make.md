### Makefile Documentation & Usage Guide

This document provides a detailed reference for all targets available in the project's `Makefile`. It is designed to help developers, product users, and platform administrators understand how to interact with the automation suite.

---

### Persona Guides

#### 1. For Developers (Building the Platform)
If you are developing the Ansible roles or adding new infrastructure features:
- Use `make dev-deploy` to test changes on your local Parallels VMs.
- Use `make native-lint` frequently to ensure code quality.
- Use `make native-test` to verify logic (e.g., API token extraction).
- Use `dev-hetzner-setup` to verify discovery logic without changing production state.

#### 2. For Product Users (Managing Applications)
If you are using this platform to manage your own applications and services:
- Use `make {dev|prod}-create-app` to deploy new applications.
- Use `make {dev|prod}-sync-apps` to move applications between environments (e.g., promotion to production).
- Use `make {dev|prod}-backup` before making major changes to your environment.
- Use `make {dev|prod}-clone-env` to spin up a new environment (e.g., for staging or testing).

#### 3. For Platform Administrators
If you are responsible for the health and consistency of the entire platform:
- Use `make {dev|prod}-hetzner-setup` to ensure all remote metadata (firewalls, rDNS, S3) is captured in the state store.
- Use `make {dev|prod}-reinstall` for disaster recovery testing or when performing clean migrations.
- Use `make native-setup` to bootstrap new administrator machines with all required dependencies and collections.

#### 4. For Neural Network Code Assistants
If you are an AI assistant helping to maintain, extend, or document this platform (see [Full Persona Guide](../AGENTS.md)):
- **Respect the Hierarchy**: Always adhere to the hierarchical playbook structure in `playbooks/` and the "State Store" pattern in `state/`.
- **Prefer the Makefile**: Use `Makefile` targets for execution to ensure consistent environment variables, inventories, and host limits.
- **Discover Before Doing**: When exploring a new part of the codebase, read the corresponding `docs/` file and the `get_file_structure` of relevant roles before suggesting changes.
- **Atomic Operations**: Aim for atomic, well-tested changes. Use `make native-test-syntax` and logic tests (in `tests/`) to verify your work before completion.
- **Documentation First**: Maintain the "discovery-to-documentation" pipeline. If you learn something new about the system, ensure it is reflected in the markdown files.
- **Treat State as Sacred**: Be careful with `state/`. Use the provided backup/restore workflows rather than manual file manipulation to preserve infrastructure integrity.

---

### Target Reference

#### Deployment
**Description**: Performs a complete installation of the Coolify controller and configures all associated workers. It includes system hardening (SSH, Firewall, Fail2Ban) and sets up the Coolify API.

**Variables**:
- `EXTRA_VARS`: (Optional) Pass additional Ansible variables (e.g., `-e coolify_root_username=admin`).

**YAML Equivalent**:
```yaml
- name: Deploy Coolify Environment
  hosts: controller, worker
  roles:
    - role: common
    - role: coolify
      when: "'controller' in group_names"
```

##### `dev-deploy`
**Raw Command**:
```bash
ansible-playbook -i inventory/ -l development playbooks/coolify/create.yml
```

##### `prod-deploy`
**Raw Command**:
```bash
ansible-playbook -i inventory/ -l production playbooks/coolify/create.yml
```

#### Backup
**Description**: Triggers a full backup of the Coolify instance. This includes a database dump, `.env` file, encryption keys, and SSH keys. The artifacts are fetched to the local `state` directory and then uploaded (encrypted) to the private S3 infrastructure storage.

**Variables**:
None (uses inventory defaults).

**YAML Equivalent**:
```yaml
- name: Backup Coolify
  hosts: controller
  tasks:
    - name: Run Backup Role
      ansible.builtin.include_role:
        name: coolify
        tasks_from: backup.yml
```

##### `dev-backup`
**Raw Command**:
```bash
ansible-playbook -i inventory/ -l development playbooks/coolify/backup.yml
```

##### `prod-backup`
**Raw Command**:
```bash
ansible-playbook -i inventory/ -l production playbooks/coolify/backup.yml
```

#### Restore
**Description**: Restores a Coolify instance from the local `state` directory. It uploads the database dump, restores SSH keys, and configures the `APP_KEY` to ensure all existing resources are accessible.

**Variables**:
None (uses local state files).

**YAML Equivalent**:
```yaml
- name: Restore Coolify
  hosts: controller
  tasks:
    - name: Run Restore Role
      ansible.builtin.include_role:
        name: coolify
        tasks_from: restore.yml
```

##### `dev-restore`
**Raw Command**:
```bash
ansible-playbook -i inventory/ -l development playbooks/coolify/restore.yml
```

##### `prod-restore`
**Raw Command**:
```bash
ansible-playbook -i inventory/ -l production playbooks/coolify/restore.yml
```

#### Hetzner Infrastructure Setup
**Description**: Verifies API connectivity and discovers infrastructure settings for Hetzner Cloud and Robot. It updates rDNS records to match hostnames and saves discovered metadata (LB, certificates, server info) to the local state store.

**Variables**:
- `HCLOUD_TOKEN`: (Env) Required for Cloud discovery.
- `HETZNER_ROBOT_USER`: (Env) Required for Robot discovery.
- `HETZNER_ROBOT_PASSWORD`: (Env) Required for Robot discovery.

**YAML Equivalent**:
```yaml
- name: Infrastructure Setup
  hosts: all
  roles:
    - role: hetzner_infra
```

##### `dev-hetzner-setup`
**Raw Command**:
```bash
ansible-playbook -i inventory/ -l development playbooks/hetzner_setup.yml
```

##### `prod-hetzner-setup`
**Raw Command**:
```bash
ansible-playbook -i inventory/ -l production playbooks/hetzner_setup.yml
```

#### Reinstall
**Description**: Orchestrates a safe reinstallation of the Coolify platform. It performs a Backup -> Uninstall -> Install -> Restore flow to ensure no data is lost during the upgrade or re-imaging.

**Variables**:
None.

**YAML Equivalent**:
```yaml
- name: Reinstall Coolify
  hosts: controller
  tasks:
    - include_role: { name: coolify, tasks_from: backup.yml }
    - include_role: { name: coolify, tasks_from: uninstall.yml }
    - include_role: { name: coolify }
    - include_role: { name: coolify, tasks_from: restore.yml }
```

##### `dev-reinstall`
**Raw Command**:
```bash
ansible-playbook -i inventory/ -l development playbooks/coolify/reinstall.yml
```

##### `prod-reinstall`
**Raw Command**:
```bash
ansible-playbook -i inventory/ -l production playbooks/coolify/reinstall.yml
```

#### Login / SSH Authentication
**Description**: Authenticates the local shell by adding the environment-specific SSH private key to the `ssh-agent`. This is a prerequisite for most targets if passwordless SSH is used.

**Variables**:
None.

##### `dev-login`
**Raw Command**:
```bash
eval $(ssh-agent -s) && ssh-add ~/.ssh/vm-worker
```

##### `prod-login`
**Raw Command**:
```bash
eval $(ssh-agent -s) && ssh-add ~/.ssh/your-key
```

#### Docker Deployment
**Description**: Runs the deployment playbook inside the Ansible Docker container. This ensures a consistent environment with all dependencies pre-installed.

**Variables**:
- `ANSIBLE_IMAGE`: (Default: `ansible-coolify`) The Docker image to use.

##### `dev-docker-deploy`
**Raw Command**:
```bash
make dev-docker-deploy
# Internally runs:
# docker run ... ansible-coolify ansible-playbook -l development playbooks/coolify/create.yml
```

##### `prod-docker-deploy`
**Raw Command**:
```bash
make prod-docker-deploy
# Internally runs:
# docker run ... ansible-coolify ansible-playbook -l production playbooks/coolify/create.yml
```

#### App Synchronization
**Description**: Synchronizes applications, services, and databases between two Coolify controllers. By default, `dev-sync-apps` pulls from production to development, and `prod-sync-apps` pushes from development to production.

**Variables**:
- `DEV_CONTROLLER`: (Env/Default) Hostname of the dev controller.
- `PROD_CONTROLLER`: (Env/Default) Hostname of the prod controller.

**YAML Equivalent**:
```yaml
# See playbooks/coolify/application/sync.yml for full logic
# This playbook involves multiple plays to fetch from source and push to target.
- name: Sync Applications
  import_playbook: playbooks/coolify/application/sync.yml
  vars:
    coolify_source_controller: "noc.example.com"
    coolify_target_controller: "controller.lan"
```

##### `dev-sync-apps`
**Raw Command**:
```bash
ansible-playbook -i inventory/ playbooks/coolify/application/sync.yml \
    -e coolify_source_controller=noc.host.uk.com -e coolify_target_controller=controller.lan
```

##### `prod-sync-apps`
**Raw Command**:
```bash
ansible-playbook -i inventory/ playbooks/coolify/application/sync.yml \
    -e coolify_source_controller=controller.lan -e coolify_target_controller=noc.host.uk.com
```

---

### Resource Management Targets

#### Resource Creation
**Description**: Declaratively creates a new resource on the target controller.

**Variables**:
- `EXTRA_VARS`: Required to specify name, project, etc.

##### `create-app`
**Example Command**:
```bash
make dev-create-app EXTRA_VARS="-e coolify_application_name=my-app -e coolify_application_project_uuid=main"
```

**YAML Equivalent**:
```yaml
- name: Create App
  hosts: controller
  roles:
    - role: coolify-application
      vars:
        coolify_application_state: create
        coolify_application_name: "my-app"
```

##### `create-service`
**Example Command**:
```bash
make dev-create-service EXTRA_VARS="-e coolify_service_name=my-redis -e coolify_service_type=redis"
```

##### `create-db`
**Example Command**:
```bash
make dev-create-db EXTRA_VARS="-e coolify_database_name=my-db -e coolify_database_type=postgresql"
```

#### Resource Restoration
**Description**: Restores a specific resource from the state store.

##### `restore-app`
**Example Command**:
```bash
make dev-restore-app EXTRA_VARS="-e coolify_application_name=my-app"
```

##### `restore-service`
**Example Command**:
```bash
make dev-restore-service EXTRA_VARS="-e coolify_service_name=my-redis"
```

##### `restore-db`
**Example Command**:
```bash
make dev-restore-db EXTRA_VARS="-e coolify_database_name=my-db"
```

#### Resource Uninstallation
**Description**: Removes a resource from the Coolify controller.

##### `uninstall-app`
**Example Command**:
```bash
make dev-uninstall-app EXTRA_VARS="-e coolify_application_name=my-app"
```

##### `uninstall-service`
**Example Command**:
```bash
make dev-uninstall-service EXTRA_VARS="-e coolify_service_name=my-redis"
```

##### `uninstall-db`
**Example Command**:
```bash
make dev-uninstall-db EXTRA_VARS="-e coolify_database_name=my-db"
```

#### Environment Management
**Description**: Operations targeting entire Coolify environments.

##### `clone-env`
**Description**: Clones an entire environment (all apps, services, and databases) within a project.
**Variables**:
- `SOURCE`: (Required) Name of the source environment.
- `TARGET`: (Required) Name of the target environment.
- `PROJECT`: (Required) Project name or UUID.

**Example Command**:
```bash
make prod-clone-env SOURCE=production TARGET=staging PROJECT=my-project
```

**YAML Equivalent**:
```yaml
- name: Clone Environment
  import_playbook: playbooks/coolify/environment/clone.yml
  vars:
    coolify_source_env_name: "production"
    coolify_target_env_name: "staging"
    coolify_project_uuid: "my-project"
```

##### `empty-env`
**Description**: Deletes all resources within a specified environment. Use with extreme caution.
**Variables**:
- `ENV`: (Required) Name of the environment to empty.
- `PROJECT`: (Required) Project name or UUID.

**Example Command**:
```bash
make dev-empty-env ENV=testing PROJECT=my-project
```

---

### Native Targets

#### System Setup
##### `native-setup`
**Description**: Installs all local dependencies (Ansible, Lint, JQ) and fetches the required Ansible collections from `requirements.yml`.

**Raw Command**:
```bash
brew install ansible ansible-lint jq yq
pip install ansible-core ...
ansible-galaxy collection install -r requirements.yml
```

#### Code Quality & Testing
##### `native-lint`
**Description**: Runs `ansible-lint` against all playbooks and roles to ensure best practices and syntax correctness.

**Raw Command**:
```bash
make native-lint
```

##### `native-test`
**Description**: Runs the full testing suite, including syntax checks, token extraction logic, and Parallels VM lifecycle tests.

**Raw Command**:
```bash
make native-test-syntax && make native-test-logic && make native-test-parallels
```
