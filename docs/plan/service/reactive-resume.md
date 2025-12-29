# reactive-resume - Test Failed

## Status: FAILED
## Tested: 2025-12-29T05:19:29+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'exited' (not running/healthy)

## Container Logs

```
{'message': 'Not found.', 'docs': 'https://coolify.io/docs'}
```

## Configuration Attempted

```yaml
service_type: reactive-resume
project: service-tests
environment: testing
server_uuid: p8sw4ssksg4ksgg848kos8w4
service_uuid: gggw8c4ogo8c8kgokcw4gg0s
```

## Service Details from API

```yaml
status: exited
fqdn: Not set
docker_compose_raw: |
services:
      reactive-resume:
        image: 'amruthpillai/reactive-resume:latest'
        environment:
          - SERVICE_URL_REACTIVERESUME_3000
          - PUBLIC_URL=$SERVICE_URL_REACTIVERESUME
          - 'STORAGE_URL=${SERVICE_URL_MINIO}/default'
          - 'DATABASE_URL=postgresql://$SERVICE_USER_POSTGRES:$SERVICE_PASSWORD_POSTGRES@postgres:5432/${POSTGRES_DB:-postgres}'
          - ACCESS_TOKEN_SECRET=$SERVICE_PASSWORD_ACCESSTOKEN
          - REFRESH_TOKEN_SECRET=$SERVICE_PASSWORD_REFRESHTOKEN
          - CHROME_TOKEN=$SERVICE_PASSWORD_CHROMETOKEN
          - 'CHROME_URL=ws://chrome:3000/chrome'
          - 'REDIS_URL=redis://redis:6379'
          - STORAGE_ENDPOINT=minio
          - STORAGE_PORT=9000
          - STORAGE_REGION=us-east-1
          - STORAGE_BUCKET=default
          - STORAGE_ACCESS_KEY=$SERVICE_USER_MINIO
          - STORAGE_SECRET_KEY=$SERVICE_PASSWORD_MINIO
          - STORAGE_USE_SSL=false
          - 'DISABLE_SIGNUPS=${SERVICE_DISABLE_SIGNUPS:-false}'
          - 'DISABLE_EMAIL_AUTH=${SERVICE_DISABLE_EMAIL_AUTH:-false}'
        depends_on:
          - postgres
          - minio
          - chrome
      postgres:
        image: 'postgres:16-alpine'
        environment:
          - 'POSTGRES_DB=${POSTGRES_DB:-postgres}'
          - POSTGRES_USER=$SERVICE_USER_POSTGRES
          - POSTGRES_PASSWORD=$SERVICE_PASSWORD_POSTGRES
        volumes:
          - 'postgres-data:/var/lib/postgresql/data'
        healthcheck:
          test:
            - CMD-SHELL
            - 'pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}'
          interval: 5s
          timeout: 20s
          retries: 10
      minio:
        image: 'ghcr.io/coollabsio/minio:RELEASE.2025-10-15T17-29-55Z'
        command: 'server /data --console-address ":9001"'
        environment:
          - MINIO_SERVER_URL=$MINIO_SERVER_URL
          - MINIO_BROWSER_REDIRECT_URL=$MINIO_BROWSER_REDIRECT_URL
          - MINIO_ROOT_USER=$SERVICE_USER_MINIO
          - MINIO_ROOT_PASSWORD=$SERVICE_PASSWORD_MINIO
        volumes:
          - 'minio-data:/data'
        healthcheck:
          test:
            - CMD
            - mc
            - ready
            - local
          interval: 5s
          timeout: 20s
          retries: 10
      chrome:
        image: 'ghcr.io/browserless/chrome:latest'
        platform: linux/amd64
        environment:
          - HEALTH=true
          - TIMEOUT=10000
          - CONCURRENT=10
          - TOKEN=$SERVICE_PASSWORD_CHROMETOKEN
      redis:
        image: 'redis:7-alpine'
        command: redis-server
        volumes:
          - 'redis_data:/data'
        healthcheck:
          test:
            - CMD
            - redis-cli
            - ping
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
2. Check Coolify documentation for reactive-resume
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=reactive-resume
   ```
