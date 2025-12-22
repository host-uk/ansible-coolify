# Ansible Coolify

[![License: EUPL-1.2](https://img.shields.io/badge/License-EUPL--1.2-blue.svg)](LICENSE)

Ansible Coolify is a comprehensive automation suite for deploying, managing, and hardening [Coolify](https://coolify.io) instances. It provides a modular, "Infrastructure as Code" approach to managing your self-hosted PaaS, supporting both cloud-based and dedicated servers.

## 🚀 Key Features

- **Automated Lifecycle**: Zero-touch installation, configuration, backup, and restoration of Coolify controllers.
- **Resource Orchestration**: Declaratively manage Applications, Databases, and Services via the Coolify API.
- **Multi-Platform Support**: Built-in support for Hetzner Cloud (HCloud), Hetzner Robot (Dedicated), and Parallels VMs (Development).
- **Security First**: Automatic system hardening including SSH lockdowns, UFW firewall configuration, and Fail2Ban integration.
- **State Store Pattern**: Critical infrastructure state (API tokens, keys, DB dumps) is persisted locally and optionally backed up to encrypted S3 storage.
- **Environment Cloning**: Easily clone entire environments (e.g., Staging to Production) with automated variable and name mapping.

## 📂 Project Structure

- `playbooks/`: Hierarchical Ansible playbooks for core operations and resource management.
- `roles/`: Reusable Ansible roles for system hardening, Coolify management, and infrastructure discovery.
- `inventory/`: Multi-environment inventory configuration.
- `docs/`: Detailed technical documentation and guides.
- `Makefile`: Unified entry point for all common operations.

## ⏱️ Quick Start

### 1. Prerequisites
- Ansible 2.15+
- Python 3.10+
- SSH access to your target servers.

### 2. Initial Setup
Copy the example inventory and update it with your server details:
```bash
cp inventory.example inventory/inventory.yml
```

### 3. Deploy
Ensure your SSH keys are in the agent and run the deployment:
```bash
make prod-deploy
```

*For more detailed instructions, see the [Quick Start Guide](docs/quick_start.md).*

## 📚 Documentation

- [Getting Started](docs/README.md)
- [Makefile Usage Guide](docs/make.md) - **Primary reference for all commands.**
- [Resource Management](docs/how_to.md) - How to add apps, DBs, and services.
- [State Management & Backups](docs/state_management.md)
- [Hetzner Integration](docs/hetzner_integration.md)

## ⚖️ License

This project is licensed under the **European Union Public Licence v1.2 (EUPL-1.2)**. See the [LICENSE](LICENSE) file for details.

