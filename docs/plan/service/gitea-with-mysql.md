# gitea-with-mysql - Test Failed

## Status: FAILED
## Tested: 2025-12-29T07:46:01+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'starting:unknown' (not running/healthy)

## Container Logs

```
{'message': 'Not found.', 'docs': 'https://coolify.io/docs'}
```

## Configuration Attempted

```yaml
service_type: gitea-with-mysql
project: service-tests
environment: testing
server_uuid: sswcwc404c4gskcsgkoockkc
service_uuid: fc8wkcsk8wogg84cgo4cw440
```

## Service Details from API

```yaml
status: starting:unknown
fqdn: Not set
docker_compose_raw: |
services:
      gitea:
        image: 'gitea/gitea:latest'
        environment:
          - SERVICE_URL_GITEA_3000
          - USER_UID=1000
          - USER_GID=1000
          - GITEA__database__DB_TYPE=mysql
          - GITEA__database__HOST=mysql
          - 'GITEA__database__NAME=${MYSQL_DATABASE-gitea}'
          - GITEA__database__USER=$SERVICE_USER_MYSQL
          - GITEA__database__PASSWD=$SERVICE_PASSWORD_MYSQL
        volumes:
          - 'gitea-data:/data'
          - 'gitea-timezone:/etc/timezone:ro'
          - 'gitea-localtime:/etc/localtime:ro'
        ports:
          - '22222:22'
        depends_on:
          mysql:
            condition: service_healthy
        healthcheck:
          test:
            - CMD
            - curl
            - '-f'
            - 'http://127.0.0.1:3000'
          interval: 2s
          timeout: 10s
          retries: 15
      mysql:
        image: 'mysql:8.0'
        volumes:
          - 'gitea-mysql-data:/var/lib/mysql'
        environment:
          - 'MYSQL_USER=${SERVICE_USER_MYSQL}'
          - 'MYSQL_PASSWORD=${SERVICE_PASSWORD_MYSQL}'
          - 'MYSQL_DATABASE=${MYSQL_DATABASE}'
          - 'MYSQL_ROOT_PASSWORD=${SERVICE_PASSWORD_MYSQLROOT}'
        healthcheck:
          test:
            - CMD
            - mysqladmin
            - ping
            - '-h'
            - 127.0.0.1
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
2. Check Coolify documentation for gitea-with-mysql
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=gitea-with-mysql
   ```
