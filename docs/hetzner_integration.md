### Hetzner Integration

This project integrates with Hetzner Cloud and Hetzner Robot for infrastructure management.

#### Collections Used

- `hetzner.hcloud`: For managing Hetzner Cloud resources.
- `community.hrobot`: For managing Hetzner Robot (baremetal) resources.

#### Inventory Management

The project uses a combined inventory approach located in `inventory/`:
- `inventory.yml`: Static inventory for development and production hosts. This is the source of truth for host definitions, including their platform and roles.
- `z_groups.config.yaml`: A constructed inventory that dynamically creates functional groups (like `controller`, `worker`) based on the `labels` and `platform` variables defined in `inventory.yml`.
- `remote_inventory`: A dynamic inventory script that:
    - Fetches Hetzner Cloud servers (using the `hetzner.hcloud.hcloud` plugin internally).
    - Fetches/Confirms metadata for Remote Services (S3, CDN, SaaS).
    - Adds a `services` host group to the inventory for infrastructure monitoring.

To use the dynamic HCloud portion, you must set the `HCLOUD_TOKEN` environment variable.

#### Infrastructure Setup Role (`hetzner_infra`)

The `hetzner_infra` role handles:
- **API Verification**: Confirms connectivity to HCloud, Robot, and S3 APIs.
- **Infrastructure Discovery**: Gathers detailed settings for servers, SSH keys, certificates, load balancers, and storage boxes.
- **State Persistence**: Saves discovered infrastructure settings to `state/{{ inventory_hostname }}/hetzner/` as JSON files.
- **rDNS Management**: Automatically sets the PTR record for both Cloud and Robot servers to match their `inventory_hostname`.
- **Cloud Firewalls** (Optional): Manages `coolify-firewall` (Disabled by default).
- **Robot Hardware Firewall** (Optional): Manages hardware firewall for baremetal servers (Disabled by default).

#### Configuration

Firewall management can be enabled by setting `hetzner_infra_manage_firewall: true`.
UFW management in the `common` role can be enabled by setting `common_manage_ufw: true`.

#### Usage

To sync the infrastructure settings with Hetzner:

```bash
make prod-hetzner-setup
```

#### Required Environment Variables

- `HCLOUD_TOKEN`: For Hetzner Cloud API.
- `HETZNER_ROBOT_USER`: For Hetzner Robot API.
- `HETZNER_ROBOT_PASSWORD`: For Hetzner Robot API.
