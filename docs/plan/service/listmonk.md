# listmonk - Test Failed

## Status: FAILED
## Tested: 2025-12-29T08:26:47+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'degraded:unhealthy' (not running/healthy)

## Container Logs

```
{'message': 'Not found.', 'docs': 'https://coolify.io/docs'}
```

## Configuration Attempted

```yaml
service_type: listmonk
project: service-tests
environment: testing
server_uuid: sswcwc404c4gskcsgkoockkc
service_uuid: y4w4w4ks84g04o0wcw4ssw08
```

## Service Details from API

```yaml
status: degraded:unhealthy
fqdn: Not set
docker_compose_raw: |
services:
      listmonk:
        image: 'listmonk/listmonk:latest'
        environment:
          - SERVICE_URL_LISTMONK_9000
          - 'LISTMONK_app__address=0.0.0.0:9000'
          - LISTMONK_db__host=postgres
          - LISTMONK_db__name=listmonk
          - LISTMONK_db__user=$SERVICE_USER_POSTGRES
          - LISTMONK_db__password=$SERVICE_PASSWORD_POSTGRES
          - LISTMONK_db__port=5432
          - TZ=Etc/UTC
        volumes:
          - 'listmonk-data:/listmonk/uploads'
        depends_on:
          postgres:
            condition: service_healthy
        healthcheck:
          test:
            - CMD
            - wget
            - '-q'
            - '--spider'
            - 'http://127.0.0.1:9000'
          interval: 5s
          timeout: 20s
          retries: 10
      listmonk-initial-database-setup:
        image: 'listmonk/listmonk:latest'
        command: './listmonk --install --yes --idempotent'
        restart: 'no'
        depends_on:
          postgres:
            condition: service_healthy
        environment:
          - LISTMONK_db__host=postgres
          - LISTMONK_db__name=listmonk
          - LISTMONK_db__user=$SERVICE_USER_POSTGRES
          - LISTMONK_db__password=$SERVICE_PASSWORD_POSTGRES
          - LISTMONK_db__port=5432
      postgres:
        image: 'postgres:latest'
        environment:
          - POSTGRES_DB=listmonk
          - POSTGRES_PASSWORD=$SERVICE_PASSWORD_POSTGRES
          - POSTGRES_USER=$SERVICE_USER_POSTGRES
        volumes:
          - 'pg-data:/var/lib/postgresql/data'
        healthcheck:
          test:
            - CMD-SHELL
            - 'pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}'
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
2. Check Coolify documentation for listmonk
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=listmonk
   ```
