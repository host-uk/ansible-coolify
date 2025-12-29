# unleash-with-postgresql - Test Failed

## Status: FAILED
## Tested: 2025-12-29T08:45:44+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'degraded:unhealthy' (not running/healthy)

## Container Logs

```
{'message': 'Not found.', 'docs': 'https://coolify.io/docs'}
```

## Configuration Attempted

```yaml
service_type: unleash-with-postgresql
project: service-tests
environment: testing
server_uuid: sswcwc404c4gskcsgkoockkc
service_uuid: ekw48ssw0c0g400s4k4cwc8o
```

## Service Details from API

```yaml
status: degraded:unhealthy
fqdn: Not set
docker_compose_raw: |
services:
      unleash:
        image: 'unleashorg/unleash-server:latest'
        environment:
          - SERVICE_URL_UNLEASH_4242
          - 'UNLEASH_URL=${SERVICE_URL_UNLEASH}'
          - 'UNLEASH_DEFAULT_ADMIN_PASSWORD=${SERVICE_PASSWORD_UNLEASH}'
          - 'DATABASE_URL=postgres://$SERVICE_USER_POSTGRES:$SERVICE_PASSWORD_POSTGRES@postgres/db'
          - DATABASE_SSL=false
          - LOG_LEVEL=warn
          - 'INIT_FRONTEND_API_TOKENS=default:default:development.unleash-insecure-frontend-api-token'
          - 'INIT_CLIENT_API_TOKENS=default:development.unleash-insecure-api-token'
        depends_on:
          postgres:
            condition: service_healthy
        command:
          - node
          - index.js
        healthcheck:
          test: 'wget --no-verbose --tries=1 --spider http://127.0.0.1:4242/health || exit 1'
          interval: 1s
          timeout: 1m
          retries: 5
          start_period: 15s
      postgres:
        image: 'postgres:15'
        volumes:
          - 'postgresql-data:/var/lib/postgresql/data'
        environment:
          - POSTGRES_USER=$SERVICE_USER_POSTGRES
          - POSTGRES_PASSWORD=$SERVICE_PASSWORD_POSTGRES
          - POSTGRES_DB=db
        healthcheck:
          test:
            - CMD
            - pg_isready
            - '--username=$SERVICE_USER_POSTGRES'
            - '--host=127.0.0.1'
            - '--port=5432'
            - '--dbname=db'
          interval: 2s
          timeout: 1m
          retries: 5
          start_period: 10s

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
2. Check Coolify documentation for unleash-with-postgresql
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=unleash-with-postgresql
   ```
