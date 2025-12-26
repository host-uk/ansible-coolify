# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ansible Coolify is an automation suite for deploying, managing, and hardening [Coolify](https://coolify.io) instances. It provides Infrastructure as Code for self-hosted PaaS management, supporting Hetzner Cloud, Hetzner Robot (dedicated servers), and Parallels VMs (development).

## Common Commands

### Setup
```bash
make native-setup           # Install dependencies (Ansible, collections, pip packages)
cp inventory.example inventory/inventory.yml  # Create inventory from template
```

### Development
```bash
make dev-deploy             # Deploy Coolify to development environment
make dev-backup             # Backup Coolify instance
make dev-restore            # Restore from local state
make dev-uninstall          # Uninstall Coolify
make dev-login              # Add dev SSH keys to ssh-agent
```

### Production
```bash
make prod-deploy            # Deploy Coolify to production
make prod-backup            # Backup production instance
make prod-restore           # Restore production from state
```

### Resource Management
```bash
make {dev,prod}-create-app EXTRA_VARS="-e coolify_application_name=my-app"
make {dev,prod}-create-db EXTRA_VARS="-e coolify_database_name=my-db -e coolify_database_type=postgresql"
make {dev,prod}-create-service EXTRA_VARS="-e coolify_service_name=my-redis -e coolify_service_type=redis"
make {dev,prod}-clone-env SOURCE=prod TARGET=staging PROJECT=my-project
make {dev,prod}-empty-env ENV=testing PROJECT=my-project
```

### Testing & Linting
```bash
make native-lint            # Run ansible-lint on playbooks and roles
make native-test            # Run full test suite (syntax + logic + parallels)
make native-test-syntax     # Syntax check only
make native-test-logic      # Test API token extraction logic
```

### Running Playbooks Directly
```bash
# Pattern: ansible-playbook -i inventory/ -l {development|production} playbooks/path/to/playbook.yml
ansible-playbook -i inventory/ -l development playbooks/coolify/create.yml
ansible-playbook -i inventory/ -l production playbooks/coolify/backup.yml
```

## Architecture

### Directory Structure
- `playbooks/`: Hierarchical playbooks organized by resource type
  - `coolify/`: Core operations (create, backup, restore, reinstall, uninstall)
  - `coolify/application/`: Application lifecycle (create, restore, uninstall, sync)
  - `coolify/database/`: Database lifecycle
  - `coolify/service/`: Service lifecycle
  - `coolify/environment/`: Environment operations (clone, empty)
- `playbooks/roles/`: Core roles
  - `common`: System hardening (SSH, UFW, Fail2Ban)
  - `coolify`: Main Coolify installation and API setup
  - `coolify-application`, `coolify-database`, `coolify-service`: Resource management
- `roles/`: Infrastructure roles
  - `hetzner_infra`: Hetzner Cloud/Robot discovery
  - `parallels_vm`: Development VM management
- `state/`: (gitignored) Local store for API tokens, SSH keys, database dumps
- `inventory/`: Multi-environment inventory configuration

### Key Patterns

**State Store**: Critical infrastructure state is persisted in `state/` directory per host. Contains API tokens, encryption keys, and database backups. Never manually edit—use backup/restore workflows.

**Environment Groups**: Inventory uses `development` and `production` groups. Always use `--limit` or the appropriate Make target (`dev-*` or `prod-*`).

**Host Labels**: Hosts are labeled by role (`controller`, `worker`, `server`, `builder`). Playbooks target these labels (e.g., `hosts: controller`).

**API Interaction**: The `coolify` role sets up API access via `api_setup.yml`. API token is extracted from Coolify's PHP tinker and stored in state.

### Deployment Flow
1. `parallels_vm` role prepares development VMs (if applicable)
2. `common` role hardens the system (SSH, firewall, fail2ban)
3. `coolify` role installs Coolify, configures API, sets up S3 backups
4. Worker/server hosts get `common` role only

## Development Guidelines

- Use Makefile targets for consistent environment and inventory handling
- Run `make native-lint` before committing changes
- Run `make native-test-syntax` to verify role syntax
- Follow the hierarchical playbook structure—don't flatten it
- Write tests in `tests/` for new logic or role enhancements
- Document discoveries in `docs/` markdown files
