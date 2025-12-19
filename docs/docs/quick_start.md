## 1. Prepare Your Bare Metal Servers

Ensure your servers are running Ubuntu 24.04 LTS (amd64). You should have SSH access to these servers as root or a user with sudo privileges.

The following servers are configured in this setup:
- `noc.host.uk.com` (Production Controller - Beszel, Sentry.io)
- `lab.snider.dev` (Development Controller)
- `de.host.uk.com` (App Server - dc14)
- `de2.host.uk.com` (App Server - dc13)
- `build.de.host.uk.com` (Docker Build server)

## 2. Configure Ansible Inventory

Update the `ansible/inventory/inventory.yml` file. This repository supports both **production** and **development** environments using Ansible groups and the `--limit` flag.

### Inventory File Example

```yaml
all:
  children:
    # Environment groups: Use these with --limit (e.g., -l production)
    production:
      hosts:
        noc.host.uk.com:
        de.host.uk.com:
        de2.host.uk.com:
        build.de.host.uk.com:
    development:
      hosts:
        lab.snider.dev:
        localhost:
        vm-worker:

    # Role-based groups
    app_servers:
      hosts:
        de.host.uk.com:
        de2.host.uk.com:
    monitoring:
      hosts:
        noc.host.uk.com:
    builders:
      hosts:
        build.de.host.uk.com:

    # Functional groups: Used by playbooks
    controller:
      hosts:
        noc.host.uk.com:
        lab.snider.dev:
          ansible_host: dev.host.uk.com
        localhost:
          ansible_connection: local
    worker:
      hosts:
        de.host.uk.com:
        de2.host.uk.com:
        build.de.host.uk.com:
        vm-worker:
          ansible_host: 192.168.1.100 # Replace with your VM IP
```

## 3. Prepare SSH Keys

Ensure your SSH public key is available at the path specified in `ansible/playbooks/roles/common/defaults/main.yml` (default is `/secrets/ssh_key.pub` when running in Docker).

## 4. Run Ansible in a Docker Container

You can run Ansible in a Docker container to ensure a consistent environment.

```shell
cd ansible
docker build -t ansible-coolify .

docker run -it --rm \
  -v ./inventory/inventory.yml:/config/inventory.yml \
  -v /path/to/your/.ssh/id_rsa:/secrets/ssh_key \
  -v /path/to/your/.ssh/id_rsa.pub:/secrets/ssh_key.pub \
  ansible-coolify
```

## 5. Run the Ansible Playbook

Inside the container (or locally), run the playbook to install Coolify and harden the servers. **Always use the `--limit` (or `-l`) flag to specify which environment you are targeting.**

### For Production
```shell
ansible-playbook -l production playbooks/playbook_install_coolify.yml
```

### For Development (Testing)
```shell
ansible-playbook -l development playbooks/playbook_install_coolify.yml
```

The Ansible playbook:
- Updates and upgrades all packages (Ubuntu 24.04).
- Installs UFW and Fail2Ban for security.
- Hardens SSH configuration.
- Installs Coolify on the controller host.
- Configures workers for Coolify communication.

## 6. Access Coolify UI

Once the playbook finishes, access Coolify at:
- **Production**: `https://noc.host.uk.com:8000`
- **Development**: `https://lab.snider.dev:8000` (or your controller's IP)

## 7. Post-Installation

Use the Coolify API or UI to further configure your infrastructure.
For `noc.host.uk.com`, you can now deploy Beszel and Sentry.io using Coolify's Docker-based deployments.
