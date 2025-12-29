# jellyfin - Test Failed

## Status: FAILED
## Tested: 2025-12-29T04:29:12+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'exited' (not running/healthy)

## Container Logs

```
{'message': 'Not found.', 'docs': 'https://coolify.io/docs'}
```

## Configuration Attempted

```yaml
service_type: jellyfin
project: service-tests
environment: testing
server_uuid: p8sw4ssksg4ksgg848kos8w4
service_uuid: z8g8c8osoko48k0kcg4swcww
```

## Service Details from API

```yaml
status: exited
fqdn: Not set
docker_compose_raw: |
services:
      jellyfin:
        image: 'lscr.io/linuxserver/jellyfin:latest'
        environment:
          - SERVICE_URL_JELLYFIN_8096
          - PUID=1000
          - PGID=1000
          - TZ=Europe/Madrid
          - JELLYFIN_PublishedServerUrl=$SERVICE_URL_JELLYFIN
        volumes:
          - 'jellyfin-config:/config'
          - 'jellyfin-tvshows:/data/tvshows'
          - 'jellyfin-movies:/data/movies'
        healthcheck:
          test:
            - CMD
            - curl
            - '-f'
            - 'http://127.0.0.1:8096'
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
2. Check Coolify documentation for jellyfin
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=jellyfin
   ```
