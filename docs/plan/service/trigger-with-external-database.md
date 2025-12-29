# trigger-with-external-database - Test Failed

## Status: FAILED
## Tested: 2025-12-29T08:44:01+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'exited' (not running/healthy)

## Container Logs

```
{'message': 'Not found.', 'docs': 'https://coolify.io/docs'}
```

## Configuration Attempted

```yaml
service_type: trigger-with-external-database
project: service-tests
environment: testing
server_uuid: sswcwc404c4gskcsgkoockkc
service_uuid: h8gc0gw8wwk00g00sg44sg80
```

## Service Details from API

```yaml
status: exited
fqdn: Not set
docker_compose_raw: |
services:
      trigger:
        image: 'ghcr.io/triggerdotdev/trigger.dev:main'
        environment:
          - SERVICE_URL_TRIGGER_3000
          - LOGIN_ORIGIN=$SERVICE_URL_TRIGGER
          - APP_ORIGIN=$SERVICE_URL_TRIGGER
          - MAGIC_LINK_SECRET=$SERVICE_PASSWORD_32_MAGIC
          - ENCRYPTION_KEY=$SERVICE_PASSWORD_32_ENCRYPTION
          - SESSION_SECRET=$SERVICE_PASSWORD_32_SESSION
          - 'DATABASE_URL=${DATABASE_URL:?}'
          - 'DIRECT_URL=${DATABASE_URL:?}'
          - RUNTIME_PLATFORM=docker-compose
          - NODE_ENV=production
          - 'AUTH_GITHUB_CLIENT_ID=${AUTH_GITHUB_CLIENT_ID}'
          - 'AUTH_GITHUB_CLIENT_SECRET=${AUTH_GITHUB_CLIENT_SECRET}'
          - 'RESEND_API_KEY=${RESEND_API_KEY}'
          - 'FROM_EMAIL=${FROM_EMAIL}'
          - 'REPLY_TO_EMAIL=${REPLY_TO_EMAIL}'
          - 'REDIS_HOST=${REDIS_HOST}'
          - 'REDIS_PORT=${REDIS_PORT}'
          - 'REDIS_USERNAME=${REDIS_USERNAME}'
          - 'REDIS_PASSWORD=${REDIS_PASSWORD}'
          - 'REDIS_TLS_DISABLED=${REDIS_TLS_DISABLED:-true}'
        healthcheck:
          test: "timeout 10s bash -c ':> /dev/tcp/127.0.0.1/3000' || exit 1"
          interval: 10s
          timeout: 5s
          retries: 5

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
2. Check Coolify documentation for trigger-with-external-database
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=trigger-with-external-database
   ```
