# Environment Helpers

This document covers the environment management playbooks for backup detection, restore, templates, and moving resources between environments.

## Overview

| Playbook | Description |
|----------|-------------|
| `backup_check.yml` | Compare local state against live API to detect changes |
| `environment/restore.yml` | Restore services from local state to Coolify |
| `template/save.yml` | Save environment as reusable template |
| `template/apply.yml` | Create services from template |
| `template/list.yml` | List available templates |
| `environment/move.yml` | Move/clone services between environments |

## Backup Detection

Compares local `state/<project>/<env>/` files against the live Coolify API to detect resources that need backup.

### Usage

```bash
# Check backup status
ansible-playbook playbooks/coolify/backup_check.yml \
  -e project=example -e env_name=production

# Auto-backup modified resources
ansible-playbook playbooks/coolify/backup_check.yml \
  -e project=example -e env_name=production \
  -e auto_backup=true
```

### Detection States

| State | Description |
|-------|-------------|
| NEW | Resources in API not in local state (need initial backup) |
| MODIFIED | Resources with changed `updated_at` timestamp |
| DELETED | Resources in local state but removed from API |
| UNCHANGED | Resources that match |

### State Directory Structure

```
state/<project>/<env>/
├── services.json           # Full service definitions
├── <service>_envs.json     # Environment variables (mode 0600)
└── last_backup.json        # Backup timestamp metadata
```

---

## Environment Restore

Restores services from local state folder back to Coolify API.

### Usage

```bash
# Dry-run (preview)
ansible-playbook playbooks/coolify/environment/restore.yml \
  -e project=example -e env_name=production \
  -e dry_run=true

# Restore services only
ansible-playbook playbooks/coolify/environment/restore.yml \
  -e project=example -e env_name=production

# Restore services + environment variables
ansible-playbook playbooks/coolify/environment/restore.yml \
  -e project=example -e env_name=production \
  -e restore_envs=true

# Override server for new resources
ansible-playbook playbooks/coolify/environment/restore.yml \
  -e project=example -e env_name=production \
  -e server_uuid=xxxxx
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `dry_run` | false | Preview without making changes |
| `restore_envs` | false | Also restore environment variables |
| `server_uuid` | (from state) | Override server for new resources |

---

## Templates

Save environment configurations as reusable templates and apply them to new environments.

### Save Template

```bash
ansible-playbook playbooks/coolify/template/save.yml \
  -e project=example -e env_name=production \
  -e template_name=my-stack
```

Creates:
```
templates/<template_name>/
├── template.yml       # Metadata (name, source, service count)
├── services.yml       # Service definitions (sanitized, no UUIDs)
└── envs/
    ├── chatwoot.yml   # User env vars (Coolify-managed excluded)
    └── redis.yml
```

### List Templates

```bash
ansible-playbook playbooks/coolify/template/list.yml
```

### Apply Template

```bash
# Dry-run
ansible-playbook playbooks/coolify/template/apply.yml \
  -e template_name=my-stack \
  -e project=example -e env_name=staging \
  -e dry_run=true

# Apply with environment variables
ansible-playbook playbooks/coolify/template/apply.yml \
  -e template_name=my-stack \
  -e project=example -e env_name=staging \
  -e apply_envs=true
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `dry_run` | false | Preview without making changes |
| `apply_envs` | false | Also apply environment variables |
| `server_uuid` | (auto) | Override server for new resources |

---

## Move Resources

Move or clone services between environments. Supports filtering by service type.

### Usage

```bash
# Move all services
ansible-playbook playbooks/coolify/environment/move.yml \
  -e source_project=example -e source_env=staging \
  -e target_project=example -e target_env=production

# Move specific service types
ansible-playbook playbooks/coolify/environment/move.yml \
  -e source_project=example -e source_env=staging \
  -e target_project=example -e target_env=production \
  -e "service_types=['chatwoot','redis']"

# Clone instead of move (keep source)
ansible-playbook playbooks/coolify/environment/move.yml \
  -e source_project=example -e source_env=staging \
  -e target_project=example -e target_env=production \
  -e keep_source=true

# Dry-run
ansible-playbook playbooks/coolify/environment/move.yml \
  -e source_project=example -e source_env=staging \
  -e target_project=example -e target_env=production \
  -e dry_run=true
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `dry_run` | false | Preview without making changes |
| `move_envs` | true | Copy environment variables |
| `keep_source` | false | Don't delete source (clone behavior) |
| `service_types` | [] | Filter by service type (empty = all) |
| `server_uuid` | (from source) | Override server for target |

### Conflict Handling

If a service type already exists in the target environment, it will be skipped. The playbook reports conflicts in the move plan.

---

## Environment Sync

For syncing/comparing environments, see `playbooks/coolify/environment/sync_test.yml` which demonstrates:

- Discovering source environment resources
- Creating matching resources in target environments
- Comparing environments to verify they match
- Saving state for backup comparison

---

## Best Practices

1. **Always backup first**: Run `backup_check.yml` with `auto_backup=true` before making changes
2. **Use dry-run**: Preview changes with `-e dry_run=true` before applying
3. **Template reusable stacks**: Save common service combinations as templates
4. **Use move for promotions**: Move services from staging to production
5. **Keep state in sync**: Run backup detection regularly to catch drift
