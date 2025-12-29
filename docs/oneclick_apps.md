# One-Click App Deployment

Deploy Coolify one-click applications with automatic shared infrastructure configuration.

## Overview

The One-Click App role automatically detects database requirements for 100+ Coolify services and configures them to use the shared infrastructure (Galera, Redis, PostgreSQL Patroni).

## Quick Start

### Deploy an Application

```bash
# Deploy Chatwoot (auto-detects PostgreSQL + Redis)
make dev-oneclick-deploy APP=chatwoot NAME=my-chatwoot

# Deploy n8n (auto-detects PostgreSQL + Redis)
make dev-oneclick-deploy APP=n8n NAME=automation

# Deploy Uptime Kuma (standalone, no database)
make dev-oneclick-deploy APP=uptime-kuma NAME=monitoring
```

### List Available Apps

```bash
# Show all supported one-click apps with their database requirements
make dev-oneclick-list
```

### Detect Database Requirements

```bash
# Check what databases an app needs before deploying
make dev-oneclick-detect APP=ghost
```

## How It Works

1. **Load Database Mappings**: Role loads `vars/database_mappings.yml`
2. **Detect Requirements**: Checks if app needs PostgreSQL, MariaDB, or Redis
3. **Create Database/User**: If needed, creates app-specific database and user
4. **Configure Environment**: Sets `DATABASE_URL`, `REDIS_URL`, etc.
5. **Deploy via Coolify API**: Creates service with pre-configured environment

## Database Mappings

### PostgreSQL Services (40+)

```yaml
postgresql_services:
  - chatwoot
  - n8n
  - gitea
  - grafana
  - hasura
  - keycloak
  - mattermost
  - metabase
  - nocodb
  - outline
  - plausible
  - posthog
  - supabase
  - umami
  - windmill
  # ... and more
```

### MariaDB/MySQL Services (20+)

```yaml
mariadb_services:
  - wordpress
  - ghost
  - nextcloud
  - drupal
  - joomla
  - matomo
  - bookstack
  - firefly
  - invoiceninja
  - kimai
  - magento
  - mediawiki
  - monica
  - prestashop
  # ... and more
```

### Redis Required Services (20+)

```yaml
redis_required_services:
  - chatwoot
  - n8n
  - ghost
  - nextcloud
  - mastodon
  - gitlab
  - discourse
  - forem
  - peertube
  - pixelfed
  - synapse
  # ... and more
```

### Standalone Services (50+)

Applications that don't require external databases:

```yaml
standalone_services:
  - uptime-kuma
  - vaultwarden
  - filebrowser
  - homepage
  - heimdall
  - homarr
  - nginx
  - traefik
  - caddy
  - code-server
  - excalidraw
  - minio
  - registry
  # ... and more
```

## Configuration

### Default Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `oneclick_service_type` | (required) | Coolify service type |
| `oneclick_app_name` | (required) | Application name |
| `oneclick_project_uuid` | (auto) | Target project UUID |
| `oneclick_environment` | (auto) | Target environment |
| `oneclick_server_uuid` | (auto) | Target server UUID |

### Shared Infrastructure Hosts

```yaml
# These are configured automatically from role defaults
galera_hostname: db.host.uk.com
redis_hostname: cache.host.uk.com
postgresql_hostname: db.postgres.host.uk.com
```

### Override Database Selection

Force specific database type:

```bash
# Force PostgreSQL even if not auto-detected
ansible-playbook -i inventory/ playbooks/coolify/oneclick/deploy.yml \
  -e oneclick_service_type=custom-app \
  -e oneclick_app_name=my-app \
  -e force_postgresql=true
```

## Environment Variables

### PostgreSQL Apps

```yaml
DATABASE_URL: postgres://user:pass@db.postgres.host.uk.com:5432/dbname
DB_HOST: db.postgres.host.uk.com
DB_PORT: 5432
DB_DATABASE: <app_name>
DB_USERNAME: <app_name>_user
DB_PASSWORD: <generated>
```

### MariaDB Apps

```yaml
DATABASE_URL: mysql://user:pass@db.host.uk.com:3306/dbname
DB_CONNECTION: mysql
DB_HOST: db.host.uk.com
DB_PORT: 3306
DB_DATABASE: <app_name>
DB_USERNAME: <app_name>_user
DB_PASSWORD: <generated>
```

### Redis Apps

```yaml
REDIS_URL: redis://:password@cache.host.uk.com:6379
REDIS_HOST: cache.host.uk.com
REDIS_PORT: 6379
REDIS_PASSWORD: <from state/redis/password.txt>
```

## Examples

### Deploy Full Application Stack

```bash
# 1. Ensure shared infrastructure is deployed
make dev-cluster-deploy

# 2. Deploy Chatwoot (customer support)
make dev-oneclick-deploy APP=chatwoot NAME=support

# 3. Deploy n8n (automation)
make dev-oneclick-deploy APP=n8n NAME=automation

# 4. Deploy Uptime Kuma (monitoring)
make dev-oneclick-deploy APP=uptime-kuma NAME=monitoring

# 5. Deploy Plausible (analytics)
make dev-oneclick-deploy APP=plausible NAME=analytics
```

### Deploy with Custom Project

```bash
ansible-playbook -i inventory/ playbooks/coolify/oneclick/deploy.yml \
  -e oneclick_service_type=n8n \
  -e oneclick_app_name=my-n8n \
  -e coolify_project_uuid=abc123 \
  -e coolify_environment=production
```

## Troubleshooting

### App Can't Connect to Database

1. Verify shared infrastructure is deployed: `make dev-cluster-status`
2. Check database credentials in state directory
3. Verify hostname resolution in app container
4. Check database exists: run status playbook for the cluster

### Unknown Service Type

If a service isn't in the mappings:

```bash
# Check if it's in any category
make dev-oneclick-detect APP=my-service

# If not found, deploy as standalone
ansible-playbook -i inventory/ playbooks/coolify/oneclick/deploy.yml \
  -e oneclick_service_type=my-service \
  -e oneclick_app_name=my-app \
  -e force_standalone=true
```

### Adding New Services

Edit `playbooks/roles/coolify-oneclick-app/vars/database_mappings.yml`:

```yaml
# Add to appropriate category
postgresql_services:
  - my-new-app  # if it needs PostgreSQL

redis_required_services:
  - my-new-app  # if it also needs Redis
```

## Files

| Path | Description |
|------|-------------|
| `playbooks/coolify/oneclick/deploy.yml` | Deploy one-click app |
| `playbooks/coolify/oneclick/list.yml` | List available apps |
| `playbooks/coolify/oneclick/detect.yml` | Detect database requirements |
| `playbooks/roles/coolify-oneclick-app/` | One-Click App role |
| `playbooks/roles/coolify-oneclick-app/vars/database_mappings.yml` | Service-to-database mappings |
| `state/oneclick/` | App-specific state |
