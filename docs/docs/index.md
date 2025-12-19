# Bare Metal Coolify Infrastructure

Infrastructure for setting up bare metal servers (Ubuntu 24.04) and Docker containers, utilizing [Coolify](https://coolify.io) as an all-in-one PaaS to self-host your own applications, databases, or services.

## Prerequisites

Before you begin, ensure you have the following:

- Bare metal or VPS servers running Ubuntu 24.04 LTS (amd64).
- SSH access to the servers.
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) (can be run via Docker).

## Infrastructure Overview

The setup currently supports the following servers:
- `noc.host.uk.com`: Production Coolify Controller, Monitoring (Beszel), and Error Tracking (Sentry.io).
- `lab.snider.dev`: Development Coolify Controller.
- `de.host.uk.com`, `de2.host.uk.com`: Application worker hosts.
- `build.de.host.uk.com`: Dedicated Docker build server.
