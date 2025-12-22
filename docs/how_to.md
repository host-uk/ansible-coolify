### How-To Guides

This document provides step-by-step instructions for common tasks in this project.

#### 1. Adding a New Application
To deploy a new application to Coolify via Ansible:
1.  **Create a Playbook**: Create a new file in `playbooks/coolify/application/` (e.g., `my-new-app.yml`).
2.  **Define the Role**:
    ```yaml
    - name: Deploy My App
      hosts: controller
      become: true
      tasks:
        - name: Setup API
          ansible.builtin.include_role:
            name: coolify
            tasks_from: api_setup.yml
        - name: Create App
          ansible.builtin.include_role:
            name: coolify-application
          vars:
            coolify_application_name: "my-app"
            coolify_application_type: "dockercompose" # or private-deploy-key
            coolify_application_docker_compose_raw: |
              version: '3'
              services:
                web:
                  image: nginx:alpine
            coolify_application_project_uuid: "your-project-uuid"
            coolify_application_server_uuid: "your-server-uuid"
    ```
3.  **Run the Playbook**:
    ```bash
    ansible-playbook -i inventory/inventory.yml playbooks/coolify/application/my-new-app.yml
    ```

#### 2. Adding a New Database
Similar to applications, use the `coolify-database` role:
```yaml
- name: Create Database
  hosts: controller
  tasks:
    - name: Setup API
      ansible.builtin.include_role:
        name: coolify
        tasks_from: api_setup.yml
    - name: Create DB
      ansible.builtin.include_role:
        name: coolify-database
      vars:
        coolify_database_type: "postgresql"
        coolify_database_body:
          name: "my-db"
          project_uuid: "..."
          server_uuid: "..."
          instant_deploy: true
```

#### 3. Registering a New Worker
1.  **Update Inventory**: Add the new host to the `worker` group in `inventory/inventory.yml`.
2.  **Run the Create Playbook**:
    ```bash
    make dev-deploy # This will register any new workers defined in the inventory
    ```

#### 4. Backing Up and Restoring
- **Backup**: `make dev-backup` fetches critical files to `state/`.
- **Restore**: `make dev-restore` uses those files to rebuild the instance.

#### 5. Cloning an Environment
To clone all resources from one environment to another (e.g., from `staging` to `production` or `de` to `lon`):
```bash
make clone-env SOURCE=staging TARGET=production PROJECT=my-project-name
```
This handles name replacements (e.g., `app-staging` becomes `app-production`) in Docker Compose files and environment variables.
