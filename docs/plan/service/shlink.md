# shlink - Test Failed

## Status: FAILED
## Tested: 2025-12-29T05:43:25+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'starting:unhealthy' (not running/healthy)

## Container Logs

```
{'message': 'Not found.', 'docs': 'https://coolify.io/docs'}
```

## Configuration Attempted

```yaml
service_type: shlink
project: service-tests
environment: testing
server_uuid: p8sw4ssksg4ksgg848kos8w4
service_uuid: uo0k8gs84w0008oswk0ssgo8
```

## Service Details from API

```yaml
status: exited
fqdn: Not set
docker_compose_raw: |
services:
      shlink:
        image: 'shlinkio/shlink:stable'
        environment:
          - SERVICE_URL_SHLINK_8080
          - 'DEFAULT_DOMAIN=${SERVICE_FQDN_SHLINK}'
          - IS_HTTPS_ENABLED=false
          - 'INITIAL_API_KEY=${SERVICE_BASE64_SHLINKAPIKEY}'
        volumes:
          - 'shlink-data:/etc/shlink/data'
        healthcheck:
          test:
            - CMD
            - curl
            - '-f'
            - 'http://127.0.0.1:8080/rest/v3/health'
          interval: 2s
          timeout: 10s
          retries: 15
      shlink-web:
        image: shlinkio/shlink-web-client
        environment:
          - SERVICE_URL_SHLINKWEB_8080
          - 'SHLINK_SERVER_API_KEY=${SERVICE_BASE64_SHLINKAPIKEY}'
          - 'SHLINK_SERVER_URL=${SERVICE_URL_SHLINK}'
        healthcheck:
          test:
            - CMD
            - curl
            - '-f'
            - 'http://127.0.0.1:8080'
          interval: 2s
          timeout: 10s
          retries: 15

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
2. Check Coolify documentation for shlink
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=shlink
   ```
