# stirling-pdf - Test Failed

## Status: FAILED
## Tested: 2025-12-29T06:12:37+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'exited' (not running/healthy)

## Container Logs

```
{'message': 'Not found.', 'docs': 'https://coolify.io/docs'}
```

## Configuration Attempted

```yaml
service_type: stirling-pdf
project: service-tests
environment: testing
server_uuid: p8sw4ssksg4ksgg848kos8w4
service_uuid: s4s88c4wswo0cgwwcw4wokc4
```

## Service Details from API

```yaml
status: exited
fqdn: Not set
docker_compose_raw: |
services:
      stirling-pdf:
        image: 'stirlingtools/stirling-pdf:latest'
        volumes:
          - 'stirling-training-data:/usr/share/tesseract-ocr/5/tessdata'
          - 'stirling-configs:/configs'
          - 'stirling-custom-files:/customFiles/'
          - 'stirling-logs:/logs/'
        environment:
          - SERVICE_URL_SPDF_8080
          - DOCKER_ENABLE_SECURITY=false
        healthcheck:
          test: 'curl --fail --silent http://127.0.0.1:8080/api/v1/info/status | grep -q "UP" || exit 1'
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
2. Check Coolify documentation for stirling-pdf
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=stirling-pdf
   ```
