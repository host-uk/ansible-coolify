# weblate - Test Failed

## Status: FAILED
## Tested: 2025-12-29T07:23:42+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'degraded:unhealthy' (not running/healthy)

## Container Logs

```
{'message': 'Not found.', 'docs': 'https://coolify.io/docs'}
```

## Configuration Attempted

```yaml
service_type: weblate
project: service-tests
environment: testing
server_uuid: sswcwc404c4gskcsgkoockkc
service_uuid: rcks8sks8gwccwgk4cgk4gss
```

## Service Details from API

```yaml
status: degraded:unhealthy
fqdn: Not set
docker_compose_raw: |
services:
      weblate:
        image: 'weblate/weblate:latest'
        environment:
          - SERVICE_URL_WEBLATE_8080
          - WEBLATE_SITE_DOMAIN=$SERVICE_URL_WEBLATE
          - 'WEBLATE_ADMIN_NAME=${WEBLATE_ADMIN_NAME:-Admin}'
          - 'WEBLATE_ADMIN_EMAIL=${WEBLATE_ADMIN_EMAIL:-admin@example.com}'
          - WEBLATE_ADMIN_PASSWORD=$SERVICE_PASSWORD_WEBLATE
          - 'DEFAULT_FROM_EMAIL=${WEBLATE_ADMIN_EMAIL:-admin@example.com}'
          - POSTGRES_PASSWORD=$SERVICE_PASSWORD_POSTGRES
          - POSTGRES_USER=$SERVICE_USER_POSTGRES
          - 'POSTGRES_DATABASE=${POSTGRES_DB:-weblate}'
          - POSTGRES_HOST=postgresql
          - POSTGRES_PORT=5432
          - REDIS_HOST=redis
          - REDIS_PORT=6379
          - REDIS_PASSWORD=$SERVICE_PASSWORD_REDIS
        volumes:
          - 'weblate-data:/app/data'
          - 'weblate-cache:/app/cache'
        healthcheck:
          test:
            - CMD
            - curl
            - '-f'
            - 'http://127.0.0.1:8080'
          interval: 2s
          timeout: 10s
          retries: 30
      postgresql:
        image: 'postgres:16-alpine'
        volumes:
          - 'postgresql-data:/var/lib/postgresql/data'
        environment:
          - POSTGRES_USER=$SERVICE_USER_POSTGRES
          - POSTGRES_PASSWORD=$SERVICE_PASSWORD_POSTGRES
          - 'POSTGRES_DB=${POSTGRES_DB:-weblate}'
        healthcheck:
          test:
            - CMD-SHELL
            - 'pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}'
          interval: 5s
          timeout: 20s
          retries: 10
      redis:
        image: 'redis:7-alpine'
        command: "--appendonly yes --requirepass ${SERVICE_PASSWORD_REDIS}\n"
        environment:
          - REDIS_PASSWORD=$SERVICE_PASSWORD_REDIS
        volumes:
          - 'weblate-redis-data:/data'
        healthcheck:
          test:
            - CMD
            - redis-cli
            - ping
          interval: 5s
          timeout: 20s
          retries: 10

```

## Environment Variables

```yaml
# Default environment variables used
# (Service-specific overrides may be needed)
```

## Possible Fixes

- [ ] Check if service requires specific environment variables
- [ ] Verify server has sufficient resources (CPU, memory, disk)
- [ ] Check if service has special port requirements
- [ ] Review container logs for specific errors
- [ ] Check if service requires external dependencies (database, redis, etc.)

## Next Steps

1. Review the error and logs above
2. Check Coolify documentation for weblate
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=weblate
   ```
