### Ansible Roles Documentation

This project uses several custom Ansible roles to modularize logic.

#### 1. `common`
Purpose: Base system configuration and security hardening.
- **Key Tasks**:
  - Set hostname and `/etc/hosts`.
  - Update and upgrade APT packages (non-interactive).
  - Install `ufw` and `fail2ban`.
  - Configure UFW to allow SSH (22), HTTP (80), and HTTPS (443).
  - Harden SSH: Disable password authentication, prohibit root login with password.
  - Deploys `public_key` to `authorized_keys`.

#### 2. `coolify`
Purpose: Lifecycle management of the Coolify control plane.
- **Key Tasks**:
  - **Install**: Downloads and executes the official Coolify installation script.
  - **API Setup**: Automatically generates and saves an API token using `php artisan tinker`.
  - **Key Setup**: Retrieves or falls back to an existing SSH private key in Coolify and obtains its public key.
  - **Server Registration**: Registers remote servers discovered via the `server` group.
  - **Backup**: Dumps the database, fetches `.env`, `APP_KEY`, and SSH keys to the local `state` directory.
  - **Restore**: Reconstructs the Coolify instance from local state artifacts.

#### 3. `coolify-application`
Purpose: Declarative management of Coolify Applications.
- **Supported Types**: `dockercompose`, `private-deploy-key`.
- **Variables**:
  - `coolify_application_state`: `create` (default) or `delete`.
  - `coolify_application_name`: Name of the application.
  - `coolify_application_envs`: List of `{key, value}` pairs for environment variables.
  - `coolify_application_instant_deploy`: Boolean to trigger deployment immediately.

#### 4. `coolify-database`
Purpose: Manage Coolify Databases (PostgreSQL, MySQL, etc.).
- **Tasks**: Handles creation and deletion of database resources via the Coolify API.

#### 5. `coolify-service`
Purpose: Manage Coolify Services (Redis, Meilisearch, etc.).
- **Tasks**: Declaratively manages service stacks via the Coolify API.

#### 6. `parallels_vm` (Legacy/Dev)
Purpose: Automate the creation and destruction of Parallels Desktop VMs on macOS for development.
- **Tools**: Uses `prlctl` to manage VM state.

#### 7. `hetzner_infra`
Purpose: Discovery and base configuration of Hetzner infrastructure.
- **Key Tasks**:
  - **API Verification**: Confirms connectivity to HCloud, Robot, and S3 APIs.
  - **Infrastructure Discovery**: Gathers settings for servers, SSH keys, certificates, load balancers, and storage boxes.
  - **rDNS Management**: Sets PTR records for Cloud and Robot servers based on `platform`.
  - **State Persistence**: Saves discovered infrastructure info to the host-specific state store.
