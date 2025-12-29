# cloudflared - Test Failed

## Status: FAILED
## Tested: 2025-12-29T03:15:08+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'degraded:unhealthy' (not running/healthy)

## Container Logs

```
{'message': 'Not found.', 'docs': 'https://coolify.io/docs'}
```

## Configuration Attempted

```yaml
service_type: cloudflared
project: service-tests
environment: testing
server_uuid: p8sw4ssksg4ksgg848kos8w4
service_uuid: p0gcgk400ggsc8c08wocw08k
```

## Service Details from API

```yaml
status: degraded:unhealthy
fqdn: Not set
docker_compose_raw: |
services:
      cloudflared:
        container_name: cloudflare-tunnel
        image: 'cloudflare/cloudflared:latest'
        restart: unless-stopped
        network_mode: host
        command: 'tunnel --no-autoupdate run'
        environment:
          - 'TUNNEL_TOKEN=${CLOUDFLARE_TUNNEL_TOKEN}'
        healthcheck:
          test:
            - CMD
            - cloudflared
            - '--version'
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
2. Check Coolify documentation for cloudflared
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=cloudflared
   ```
