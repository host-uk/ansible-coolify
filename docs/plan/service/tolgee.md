# tolgee - Test Failed

## Status: FAILED
## Tested: 2025-12-29T06:36:55+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'unknown' (not running/healthy)

## Container Logs

```
{'message': 'Not found.', 'docs': 'https://coolify.io/docs'}
```

## Configuration Attempted

```yaml
service_type: tolgee
project: service-tests
environment: testing
server_uuid: p8sw4ssksg4ksgg848kos8w4
service_uuid: lwo40gwok4088gco4w4occc8
```

## Service Details from API

```yaml
status: exited
fqdn: Not set
docker_compose_raw: |
services:
      tolgee:
        image: tolgee/tolgee
        environment:
          - SERVICE_URL_TOLGEE_8080
          - TOLGEE_AUTHENTICATION_ENABLED=true
          - TOLGEE_AUTHENTICATION_INITIAL_PASSWORD=$SERVICE_PASSWORD_TOLGEE
          - TOLGEE_AUTHENTICATION_INITIAL_USERNAME=admin
          - TOLGEE_AUTHENTICATION_JWT_SECRET=$SERVICE_PASSWORD_JWT
          - TOLGEE_POSTGRES_AUTOSTART_ENABLED=false
          - 'SPRING_DATASOURCE_URL=jdbc:postgresql://postgresql:5432/${POSTGRES_DB:-tolgee}'
          - 'SPRING_DATASOURCE_USERNAME=${SERVICE_USER_POSTGRESQL}'
          - 'SPRING_DATASOURCE_PASSWORD=${SERVICE_PASSWORD_POSTGRESQL}'
        volumes:
          - 'tolgee-data:/data'
        healthcheck:
          test:
            - CMD
            - wget
            - '-q'
            - '--spider'
            - 'http://127.0.0.1:8080'
          interval: 5s
          timeout: 20s
          retries: 10
        depends_on:
          postgresql:
            condition: service_healthy
      postgresql:
        image: 'postgres:16-alpine'
        volumes:
          - 'tolgee-postgresql-data:/var/lib/postgresql/data'
        environment:
          - 'POSTGRES_USER=${SERVICE_USER_POSTGRESQL}'
          - 'POSTGRES_PASSWORD=${SERVICE_PASSWORD_POSTGRESQL}'
          - 'POSTGRES_DB=${POSTGRESQL_DATABASE:-tolgee}'
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
2. Check Coolify documentation for tolgee
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=tolgee
   ```
