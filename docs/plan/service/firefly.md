# firefly - Test Failed

## Status: FAILED
## Tested: 2025-12-29T03:47:25+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'exited' (not running/healthy)

## Container Logs

```
{'message': 'Not found.', 'docs': 'https://coolify.io/docs'}
```

## Configuration Attempted

```yaml
service_type: firefly
project: service-tests
environment: testing
server_uuid: p8sw4ssksg4ksgg848kos8w4
service_uuid: z80swwoook4kg04sg44gg0k8
```

## Service Details from API

```yaml
status: exited
fqdn: Not set
docker_compose_raw: |
services:
      firefly:
        image: 'fireflyiii/core:latest'
        environment:
          - SERVICE_URL_FIREFLY_8080
          - APP_KEY=$SERVICE_BASE64_APPKEY
          - DB_HOST=mysql
          - DB_PORT=3306
          - DB_CONNECTION=mysql
          - 'DB_DATABASE=${MYSQL_DATABASE:-firefly}'
          - DB_USERNAME=$SERVICE_USER_MYSQL
          - DB_PASSWORD=$SERVICE_PASSWORD_MYSQL
          - STATIC_CRON_TOKEN=$SERVICE_BASE64_CRONTOKEN
          - 'TRUSTED_PROXIES=*'
        volumes:
          - 'firefly-upload:/var/www/html/storage/upload'
        healthcheck:
          test:
            - CMD
            - curl
            - '-f'
            - 'http://127.0.0.1:8080'
          interval: 5s
          timeout: 20s
          retries: 10
        depends_on:
          mysql:
            condition: service_healthy
      mysql:
        image: 'mariadb:11'
        environment:
          - 'MYSQL_USER=${SERVICE_USER_MYSQL}'
          - 'MYSQL_PASSWORD=${SERVICE_PASSWORD_MYSQL}'
          - 'MYSQL_DATABASE=${MYSQL_DATABASE:-firefly}'
          - 'MYSQL_ROOT_PASSWORD=${SERVICE_PASSWORD_MYSQLROOT}'
        healthcheck:
          test:
            - CMD
            - mariadb-admin
            - ping
            - '-h'
            - 127.0.0.1
            - '-uroot'
            - '-p${SERVICE_PASSWORD_MYSQLROOT}'
          interval: 5s
          timeout: 20s
          retries: 10
        volumes:
          - 'firefly-mysql-data:/var/lib/mysql'
      cron:
        image: alpine
        entrypoint:
          - /entrypoint.sh
        volumes:
          -
            type: bind
            source: ./entrypoint.sh
            target: /entrypoint.sh
        environment:
          - STATIC_CRON_TOKEN=$SERVICE_BASE64_CRONTOKEN
        healthcheck:
          test:
            - CMD-SHELL
            - 'ls /entrypoint.sh || exit 1'
          interval: 30s
          timeout: 10s
          retries: 3
          start_period: 40s

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
2. Check Coolify documentation for firefly
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=firefly
   ```
