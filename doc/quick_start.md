### Quick Start Guide

This guide will help you get up and running with the Coolify automation platform.

#### 1. Prerequisites

- **macOS** (for development with Parallels) or **Linux** (for production)
- **Ansible** installed natively or via Docker
- **Docker & Docker Compose**
- **SSH Keys** generated and available in `~/.ssh/`

#### 2. Configuration

Update `inventory/inventory.yml` with your server details. You can use `inventory.example` in the project root as a template by copying it:
```bash
cp inventory.example inventory/inventory.yml
```

#### 3. Providing Custom SSH Keys

By default, the system looks for keys in `~/.ssh/`. You can customize this in your inventory:

##### Production
In the `production.vars` section:
```yaml
ansible_ssh_private_key_file: "~/.ssh/your-custom-key"
coolify_private_key_path: "~/.ssh/your-custom-key"
public_key: "{{ lookup('file', lookup('env', 'HOME') + '/.ssh/your-custom-key.pub', errors='ignore') }}"
```

##### Development
In the `development.vars` section:
```yaml
coolify_private_key_path: "~/.ssh/controller.lan"
public_key: "{{ lookup('file', lookup('env', 'HOME') + '/.ssh/controller.lan.pub', errors='ignore') }}"
```
For individual hosts in development:
```yaml
controller.lan:
  ansible_ssh_private_key_file: ~/.ssh/controller.lan
app-server.lan:
  ansible_ssh_private_key_file: ~/.ssh/app-server.lan
builder.lan:
  ansible_ssh_private_key_file: ~/.ssh/builder.lan
```

#### 4. Development Environment Automation

When running the development deployment for the first time:
1. The system automatically checks if the required SSH keys (e.g., `~/.ssh/controller.lan`) exist for each host.
2. If they are missing, **passwordless RSA keypairs** are generated automatically.
3. Parallels VMs are configured to use **macOS System Keys**, ensuring smooth interaction with the host system.

#### 5. Deployment

##### Using Docker (Recommended)
```bash
make up
make shell
ansible-playbook -l production playbooks/coolify/create.yml
```

##### Using Native Ansible
```bash
# Production
make prod-deploy

# Development
make dev-deploy
```
