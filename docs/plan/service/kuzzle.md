# kuzzle - Test Failed

## Status: FAILED
## Tested: 2025-12-29T04:41:34+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'exited' (not running/healthy)

## Container Logs

```
{'message': 'Not found.', 'docs': 'https://coolify.io/docs'}
```

## Configuration Attempted

```yaml
service_type: kuzzle
project: service-tests
environment: testing
server_uuid: p8sw4ssksg4ksgg848kos8w4
service_uuid: mosoc4gsw04o00ksw4o0skk4
```

## Service Details from API

```yaml
status: exited
fqdn: Not set
docker_compose_raw: |
services:
      redis:
        image: 'redis:7-alpine'
        command: 'redis-server --appendonly yes'
        volumes:
          - 'elastic-redis-data:/data'
        healthcheck:
          test:
            - CMD
            - redis-cli
            - ping
          interval: 5s
          timeout: 20s
          retries: 10
      elasticsearch:
        image: 'kuzzleio/elasticsearch:7'
        healthcheck:
          test:
            - CMD
            - curl
            - '-f'
            - 'http://127.0.0.1:9200'
          interval: 2s
          timeout: 2s
          retries: 10
        ulimits:
          nofile: 65536
      kuzzle:
        image: 'kuzzleio/kuzzle:latest'
        environment:
          - SERVICE_URL_KUZZLE_7512
          - 'kuzzle_services__storageEngine__client__node=http://elasticsearch:9200'
          - kuzzle_services__storageEngine__commonMapping__dynamic=true
          - kuzzle_services__internalCache__node__host=redis
          - kuzzle_services__memoryStorage__node__host=redis
          - kuzzle_server__protocols__mqtt__enabled=true
          - kuzzle_server__protocols__mqtt__developmentMode=false
          - kuzzle_limits__loginsPerSecond=50
          - NODE_ENV=production
          - 'DEBUG=${DEBUG:-kuzzle:cluster:sync}'
          - 'DEBUG_DEPTH=${DEBUG_DEPTH:-0}'
          - 'DEBUG_MAX_ARRAY_LENGTH=${DEBUG_MAX_ARRAY:-100}'
          - 'DEBUG_EXPAND=${DEBUG_EXPAND:-off}'
          - 'DEBUG_SHOW_HIDDEN={$DEBUG_SHOW_HIDDEN:-on}'
          - 'DEBUG_COLORS=${DEBUG_COLORS:-on}'
        cap_add:
          - SYS_PTRACE
        ulimits:
          nofile: 65536
        sysctls:
          - net.core.somaxconn=8192
        healthcheck:
          test:
            - CMD
            - curl
            - '-f'
            - 'http://127.0.0.1:7512/_healthcheck'
          timeout: 1s
          interval: 2s
          retries: 30
        depends_on:
          redis:
            condition: service_healthy
          elasticsearch:
            condition: service_healthy

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
2. Check Coolify documentation for kuzzle
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=kuzzle
   ```
