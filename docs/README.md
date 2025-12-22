### Coolify Automation with Ansible

This project provides a comprehensive Ansible-based automation suite for installing, configuring, and managing [Coolify](https://coolify.io/) instances and their resources (Applications, Databases, Services).

#### Architecture Overview

- **Controller**: The main Coolify instance.
- **Workers**: Remote servers managed by the Coolify controller.
- **State Store**: A local directory (`state`) used to persist critical information like API tokens, database dumps, and SSH keys.
- **Hierarchical Playbooks**: Playbooks are organized by resource type (application, database, service) and action (create, restore, uninstall).

#### Directory Structure

- ``
    - `inventory/`: Server inventory definitions for production and development.
    - `playbooks/`: Organized by resource type.
        - `coolify/`: Core Coolify operations (install, backup, restore).
        - `coolify/application/`: Application-specific tasks.
        - `coolify/database/`: Database-specific tasks.
        - `coolify/service/`: Service-specific tasks.
    - `roles/`: Reusable logic for system hardening and Coolify management.
    - `state/`: (Ignored by git) Local store for host-specific state and backups.
- `docs/`: Project documentation.
- `Makefile`: Entry point for common operations.
- `inventory.example`: Template for the server inventory.

#### Prerequisites

- Ansible 2.15+
- Python 3.10+
- SSH access to target servers (root recommended).

#### Getting Started

1.  **Install dependencies**:
    ```bash
    make setup-native
    ```

2.  **Configure Inventory**:
    Copy `inventory.example` to `inventory/inventory.yml` and edit it with your server details.

3.  **Deploy Coolify**:
    ```bash
    make dev-deploy
    ```

#### Persona Guides

The project defines clear personas to guide interaction with the platform:
1.  **Developers**: For those building the platform logic.
2.  **Product Users**: For managing applications and services.
3.  **Platform Administrators**: For infrastructure and state management.
4.  **Neural Network Code Assistants**: Guidelines for AI-driven development and collaboration (see [Persona: Assistant](../AGENTS.md)).

#### Key Features

- **Automated Installation**: Zero-touch installation of Coolify with predefined admin credentials.
- **System Hardening**: The `common` role applies SSH hardening, UFW firewall rules, and Fail2Ban.
- **State Persistence**: Critical application keys and database backups are fetched locally to ensure recoverability.
- **Resource Cloning**: Support for cloning environments and applications across different servers or regions.
- **Worker Registration**: Automatically registers worker nodes into the Coolify controller.
- **S3 Integration**: Support for both private (infrastructure backup) and public (application storage) buckets on Hetzner Object Storage.
