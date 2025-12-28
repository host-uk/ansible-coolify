# Coolify API Ansible Modules

Custom Ansible modules for managing Coolify resources via its REST API.

## Overview

These modules provide idempotent resource management for Coolify, allowing infrastructure-as-code management of:

- Private Keys (SSH keys for server access)
- Projects and Environments
- Applications (various deployment types)
- Databases (PostgreSQL, MySQL, Redis, etc.)
- Services (one-click services like Redis, Plausible, etc.)

## Module Location

Modules are located in `playbooks/roles/coolify/library/`:

```
playbooks/roles/coolify/library/
├── coolify_private_key.py
├── coolify_project.py
├── coolify_application.py
├── coolify_database.py
└── coolify_service.py
```

## Common Parameters

All modules share these authentication parameters:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `api_url` | Yes | Coolify API base URL (e.g., `http://coolify.example.com/api/v1`) |
| `api_token` | Yes | API token for authentication |

## coolify_private_key

Manages SSH private keys in Coolify for server authentication.

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `state` | No | `present` | `present` or `absent` |
| `name` | Yes | - | Key name |
| `uuid` | No | - | Key UUID (for updates/deletion) |
| `description` | No | - | Key description |
| `private_key` | Yes* | - | Private key content (required for `present`) |

### Examples

```yaml
# Create a private key
- name: Register SSH key
  coolify_private_key:
    api_url: "{{ coolify_api_url }}"
    api_token: "{{ coolify_api_token }}"
    state: present
    name: "production-key"
    description: "SSH key for production servers"
    private_key: "{{ lookup('file', '~/.ssh/production_key') }}"
  register: key_result

# Delete a private key
- name: Remove SSH key
  coolify_private_key:
    api_url: "{{ coolify_api_url }}"
    api_token: "{{ coolify_api_token }}"
    state: absent
    uuid: "{{ key_uuid }}"
```

## coolify_project

Manages Coolify projects and their environments.

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `state` | No | `present` | `present` or `absent` |
| `name` | Yes | - | Project name |
| `uuid` | No | - | Project UUID (for updates/deletion) |
| `description` | No | - | Project description |
| `environments` | No | - | List of environment names to create |

### Examples

```yaml
# Create a project with environments
- name: Create project
  coolify_project:
    api_url: "{{ coolify_api_url }}"
    api_token: "{{ coolify_api_token }}"
    state: present
    name: "my-application"
    description: "Main application project"
    environments:
      - production
      - staging
      - development
  register: project_result

# Delete a project
- name: Remove project
  coolify_project:
    api_url: "{{ coolify_api_url }}"
    api_token: "{{ coolify_api_token }}"
    state: absent
    uuid: "{{ project_uuid }}"
```

## coolify_application

Manages Coolify applications with support for multiple source types.

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `state` | No | `present` | `present`, `absent`, `started`, `stopped`, `restarted`, `deployed` |
| `name` | No | - | Application name |
| `uuid` | No | - | Application UUID |
| `type` | Yes* | - | Application type (required for `present`) |
| `project_uuid` | Yes* | - | Project UUID (required for `present`) |
| `environment_name` | No | `production` | Environment name |
| `server_uuid` | Yes* | - | Server UUID (required for `present`) |
| `destination_uuid` | No | - | Destination UUID |
| `instant_deploy` | No | `false` | Deploy immediately after creation |

### Application Types

| Type | Description | Required Parameters |
|------|-------------|---------------------|
| `public` | Public Git repository | `git_repository`, `git_branch` |
| `private-github-app` | Private repo via GitHub App | `git_repository`, `git_branch`, `github_app_uuid` |
| `private-deploy-key` | Private repo via deploy key | `git_repository`, `git_branch`, `private_key_uuid` |
| `dockerfile` | Custom Dockerfile | `git_repository`, `git_branch`, `dockerfile` |
| `dockerimage` | Pre-built Docker image | `docker_registry_image_name` |
| `dockercompose` | Docker Compose file | `git_repository`, `git_branch`, `docker_compose_location` |

### Examples

```yaml
# Deploy from public repository
- name: Create public app
  coolify_application:
    api_url: "{{ coolify_api_url }}"
    api_token: "{{ coolify_api_token }}"
    state: present
    type: public
    project_uuid: "{{ project_uuid }}"
    server_uuid: "{{ server_uuid }}"
    git_repository: "https://github.com/user/repo"
    git_branch: "main"
    instant_deploy: true
  register: app_result

# Deploy from Docker image
- name: Create Docker image app
  coolify_application:
    api_url: "{{ coolify_api_url }}"
    api_token: "{{ coolify_api_token }}"
    state: present
    type: dockerimage
    project_uuid: "{{ project_uuid }}"
    server_uuid: "{{ server_uuid }}"
    docker_registry_image_name: "nginx:latest"

# Start/stop/restart application
- name: Stop application
  coolify_application:
    api_url: "{{ coolify_api_url }}"
    api_token: "{{ coolify_api_token }}"
    state: stopped
    uuid: "{{ app_uuid }}"

# Deploy application
- name: Deploy application
  coolify_application:
    api_url: "{{ coolify_api_url }}"
    api_token: "{{ coolify_api_token }}"
    state: deployed
    uuid: "{{ app_uuid }}"
```

## coolify_database

Manages Coolify databases with support for 8 database types.

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `state` | No | `present` | `present`, `absent`, `started`, `stopped`, `restarted` |
| `name` | No | - | Database name |
| `uuid` | No | - | Database UUID |
| `type` | Yes* | - | Database type (required for `present`) |
| `project_uuid` | Yes* | - | Project UUID (required for `present`) |
| `environment_name` | No | `production` | Environment name |
| `server_uuid` | Yes* | - | Server UUID (required for `present`) |
| `destination_uuid` | No | - | Destination UUID |
| `instant_deploy` | No | `false` | Deploy immediately after creation |

### Database Types

| Type | Description | Version Parameter |
|------|-------------|-------------------|
| `postgresql` | PostgreSQL | `postgres_version` (15, 14, 13, 12) |
| `mysql` | MySQL | `mysql_version` (8.0, 5.7) |
| `mariadb` | MariaDB | `mariadb_version` (11, 10) |
| `mongodb` | MongoDB | `mongodb_version` (7, 6, 5, 4) |
| `redis` | Redis | `redis_version` (7, 6) |
| `keydb` | KeyDB | `keydb_version` |
| `dragonfly` | Dragonfly | `dragonfly_version` |
| `clickhouse` | ClickHouse | `clickhouse_version` (24, 23) |

### Examples

```yaml
# Create PostgreSQL database
- name: Create database
  coolify_database:
    api_url: "{{ coolify_api_url }}"
    api_token: "{{ coolify_api_token }}"
    state: present
    type: postgresql
    name: "app-database"
    project_uuid: "{{ project_uuid }}"
    server_uuid: "{{ server_uuid }}"
    postgres_version: "15"
    postgres_user: "appuser"
    postgres_password: "{{ db_password }}"
    postgres_db: "appdb"
    instant_deploy: true
  register: db_result

# Create Redis cache
- name: Create Redis
  coolify_database:
    api_url: "{{ coolify_api_url }}"
    api_token: "{{ coolify_api_token }}"
    state: present
    type: redis
    name: "app-cache"
    project_uuid: "{{ project_uuid }}"
    server_uuid: "{{ server_uuid }}"
    redis_version: "7"
    redis_password: "{{ redis_password }}"

# Stop database
- name: Stop database
  coolify_database:
    api_url: "{{ coolify_api_url }}"
    api_token: "{{ coolify_api_token }}"
    state: stopped
    uuid: "{{ db_uuid }}"
```

## coolify_service

Manages Coolify one-click services (90+ available services).

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `state` | No | `present` | `present`, `absent`, `started`, `stopped`, `restarted` |
| `name` | No | - | Service name |
| `uuid` | No | - | Service UUID |
| `type` | Yes* | - | Service type (required for `present`) |
| `project_uuid` | Yes* | - | Project UUID (required for `present`) |
| `environment_name` | No | `production` | Environment name |
| `server_uuid` | Yes* | - | Server UUID (required for `present`) |
| `destination_uuid` | No | - | Destination UUID |
| `instant_deploy` | No | `false` | Deploy immediately after creation |

### Available Service Types

Common services include:

| Category | Services |
|----------|----------|
| Analytics | `plausible`, `umami`, `fathom`, `matomo` |
| Databases | `supabase`, `appwrite`, `pocketbase` |
| CMS | `ghost`, `wordpress`, `strapi`, `directus` |
| Monitoring | `grafana`, `uptime-kuma`, `glances` |
| Communication | `mattermost`, `rocketchat`, `chatwoot` |
| Storage | `minio`, `filebrowser`, `nextcloud` |
| CI/CD | `gitea`, `gitlab`, `drone`, `jenkins` |
| Other | `n8n`, `nocodb`, `baserow`, `metabase` |

See the full list in the module source or Coolify documentation.

### Examples

```yaml
# Deploy Plausible Analytics
- name: Create Plausible
  coolify_service:
    api_url: "{{ coolify_api_url }}"
    api_token: "{{ coolify_api_token }}"
    state: present
    type: plausible
    name: "analytics"
    project_uuid: "{{ project_uuid }}"
    server_uuid: "{{ server_uuid }}"
    instant_deploy: true
  register: service_result

# Deploy Uptime Kuma
- name: Create monitoring
  coolify_service:
    api_url: "{{ coolify_api_url }}"
    api_token: "{{ coolify_api_token }}"
    state: present
    type: uptime-kuma
    name: "monitoring"
    project_uuid: "{{ project_uuid }}"
    server_uuid: "{{ server_uuid }}"

# Stop service
- name: Stop service
  coolify_service:
    api_url: "{{ coolify_api_url }}"
    api_token: "{{ coolify_api_token }}"
    state: stopped
    uuid: "{{ service_uuid }}"
```

## Return Values

All modules return:

| Key | Type | Description |
|-----|------|-------------|
| `changed` | bool | Whether a change was made |
| `uuid` | string | Resource UUID (for created resources) |
| `data` | dict | Full API response data |
| `msg` | string | Status message |

## Error Handling

Modules will fail with descriptive error messages on:

- Authentication failures (invalid token)
- Resource not found (invalid UUID)
- Validation errors (missing required parameters)
- API errors (server-side issues)

Example error handling:

```yaml
- name: Create resource
  coolify_application:
    # ... parameters
  register: result
  failed_when: false

- name: Handle failure
  debug:
    msg: "Failed: {{ result.msg }}"
  when: result.failed
```

## API Reference

These modules are built against the Coolify API v1. Full API documentation is available in `docs/apis/coolify-openapi.yaml`.

Key endpoints used:

| Module | Endpoints |
|--------|-----------|
| `coolify_private_key` | `/security/keys` |
| `coolify_project` | `/projects`, `/projects/{uuid}/environments` |
| `coolify_application` | `/applications`, `/applications/{uuid}/*` |
| `coolify_database` | `/databases`, `/databases/{uuid}/*` |
| `coolify_service` | `/services`, `/services/{uuid}/*` |
