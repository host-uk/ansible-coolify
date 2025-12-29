# trigger - Test Failed

## Status: FAILED
## Tested: 2025-12-29T08:38:43+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'degraded:unhealthy' (not running/healthy)

## Container Logs

```
{'message': 'Not found.', 'docs': 'https://coolify.io/docs'}
```

## Configuration Attempted

```yaml
service_type: trigger
project: service-tests
environment: testing
server_uuid: sswcwc404c4gskcsgkoockkc
service_uuid: p8c0gwkgkkwwskc00o4scsk8
```

## Service Details from API

```yaml
status: degraded:unhealthy
fqdn: Not set
docker_compose_raw: |
x-common-env:
      REMIX_APP_PORT: 3000
      NODE_ENV: production
      RUNTIME_PLATFORM: docker-compose
      V3_ENABLED: true
      INTERNAL_OTEL_TRACE_DISABLED: 1
      INTERNAL_OTEL_TRACE_LOGGING_ENABLED: 0
      POSTGRES_USER: $SERVICE_USER_POSTGRES
      POSTGRES_PASSWORD: $SERVICE_PASSWORD_POSTGRES
      POSTGRES_DB: '${POSTGRES_DB:-trigger}'
      MAGIC_LINK_SECRET: $SERVICE_PASSWORD_32_MAGIC
      SESSION_SECRET: $SERVICE_PASSWORD_32_SESSION
      ENCRYPTION_KEY: $SERVICE_PASSWORD_32_ENCRYPTION
      PROVIDER_SECRET: $SERVICE_PASSWORD_64_PROVIDER
      COORDINATOR_SECRET: $SERVICE_PASSWORD_64_COORDINATOR
      DATABASE_HOST: 'postgresql:5432'
      DATABASE_URL: 'postgres://$SERVICE_USER_POSTGRES:$SERVICE_PASSWORD_POSTGRES@postgresql:5432/$POSTGRES_DB?sslmode=disable'
      DIRECT_URL: 'postgres://$SERVICE_USER_POSTGRES:$SERVICE_PASSWORD_POSTGRES@postgresql:5432/$POSTGRES_DB?sslmode=disable'
      REDIS_HOST: redis
      REDIS_PORT: 6379
      REDIS_TLS_DISABLED: true
      COORDINATOR_HOST: 127.0.0.1
      COORDINATOR_PORT: 9020
      WHITELISTED_EMAILS: ''
      ADMIN_EMAILS: ''
      DEFAULT_ORG_EXECUTION_CONCURRENCY_LIMIT: 300
      DEFAULT_ENV_EXECUTION_CONCURRENCY_LIMIT: 100
      DEPLOY_REGISTRY_HOST: docker.io
      DEPLOY_REGISTRY_NAMESPACE: trigger
      REGISTRY_HOST: '${DEPLOY_REGISTRY_HOST}'
      REGISTRY_NAMESPACE: '${DEPLOY_REGISTRY_NAMESPACE}'
      AUTH_GITHUB_CLIENT_ID: '${AUTH_GITHUB_CLIENT_ID}'
      AUTH_GITHUB_CLIENT_SECRET: '${AUTH_GITHUB_CLIENT_SECRET}'
      RESEND_API_KEY: '${RESEND_API_KEY}'
      FROM_EMAIL: '${FROM_EMAIL}'
      REPLY_TO_EMAIL: '${REPLY_TO_EMAIL}'
      LOGIN_ORIGIN: $SERVICE_URL_TRIGGER_3000
      APP_ORIGIN: $SERVICE_URL_TRIGGER_3000
      DEV_OTEL_EXPORTER_OTLP_ENDPOINT: $SERVICE_URL_TRIGGER_3000/otel
      OTEL_EXPORTER_OTLP_ENDPOINT: $SERVICE_URL_TRIGGER_3000/otel
      ELECTRIC_ORIGIN: 'http://electric:3000'
    services:
      trigger:
        image: 'ghcr.io/triggerdotdev/trigger.dev:v3'
        environment:
          SERVICE_URL_TRIGGER_3000: ''
          REMIX_APP_PORT: 3000
          NODE_ENV: production
          RUNTIME_PLATFORM: docker-compose
          V3_ENABLED: true
          INTERNAL_OTEL_TRACE_DISABLED: 1
          INTERNAL_OTEL_TRACE_LOGGING_ENABLED: 0
          POSTGRES_USER: $SERVICE_USER_POSTGRES
          POSTGRES_PASSWORD: $SERVICE_PASSWORD_POSTGRES
          POSTGRES_DB: '${POSTGRES_DB:-trigger}'
          MAGIC_LINK_SECRET: $SERVICE_PASSWORD_32_MAGIC
          SESSION_SECRET: $SERVICE_PASSWORD_32_SESSION
          ENCRYPTION_KEY: $SERVICE_PASSWORD_32_ENCRYPTION
          PROVIDER_SECRET: $SERVICE_PASSWORD_64_PROVIDER
          COORDINATOR_SECRET: $SERVICE_PASSWORD_64_COORDINATOR
          DATABASE_HOST: 'postgresql:5432'
          DATABASE_URL: 'postgres://$SERVICE_USER_POSTGRES:$SERVICE_PASSWORD_POSTGRES@postgresql:5432/$POSTGRES_DB?sslmode=disable'
          DIRECT_URL: 'postgres://$SERVICE_USER_POSTGRES:$SERVICE_PASSWORD_POSTGRES@postgresql:5432/$POSTGRES_DB?sslmode=disable'
          REDIS_HOST: redis
          REDIS_PORT: 6379
          REDIS_TLS_DISABLED: true
          COORDINATOR_HOST: 127.0.0.1
          COORDINATOR_PORT: 9020
          WHITELISTED_EMAILS: ''
          ADMIN_EMAILS: ''
          DEFAULT_ORG_EXECUTION_CONCURRENCY_LIMIT: 300
          DEFAULT_ENV_EXECUTION_CONCURRENCY_LIMIT: 100
          DEPLOY_REGISTRY_HOST: docker.io
          DEPLOY_REGISTRY_NAMESPACE: trigger
          REGISTRY_HOST: '${DEPLOY_REGISTRY_HOST}'
          REGISTRY_NAMESPACE: '${DEPLOY_REGISTRY_NAMESPACE}'
          AUTH_GITHUB_CLIENT_ID: '${AUTH_GITHUB_CLIENT_ID}'
          AUTH_GITHUB_CLIENT_SECRET: '${AUTH_GITHUB_CLIENT_SECRET}'
          RESEND_API_KEY: '${RESEND_API_KEY}'
          FROM_EMAIL: '${FROM_EMAIL}'
          REPLY_TO_EMAIL: '${REPLY_TO_EMAIL}'
          LOGIN_ORIGIN: $SERVICE_URL_TRIGGER_3000
          APP_ORIGIN: $SERVICE_URL_TRIGGER_3000
          DEV_OTEL_EXPORTER_OTLP_ENDPOINT: $SERVICE_URL_TRIGGER_3000/otel
          OTEL_EXPORTER_OTLP_ENDPOINT: $SERVICE_URL_TRIGGER_3000/otel
          ELECTRIC_ORIGIN: 'http://electric:3000'
        depends_on:
          postgresql:
            condition: service_healthy
          redis:
            condition: service_healthy
          electric:
            condition: service_healthy
        healthcheck:
          test: "timeout 10s bash -c ':> /dev/tcp/127.0.0.1/3000' || exit 1"
          interval: 10s
          timeout: 5s
          retries: 5
      electric:
        image: electricsql/electric
        environment:
          REMIX_APP_PORT: 3000
          NODE_ENV: production
          RUNTIME_PLATFORM: docker-compose
          V3_ENABLED: true
          INTERNAL_OTEL_TRACE_DISABLED: 1
          INTERNAL_OTEL_TRACE_LOGGING_ENABLED: 0
          POSTGRES_USER: $SERVICE_USER_POSTGRES
          POSTGRES_PASSWORD: $SERVICE_PASSWORD_POSTGRES
          POSTGRES_DB: '${POSTGRES_DB:-trigger}'
          MAGIC_LINK_SECRET: $SERVICE_PASSWORD_32_MAGIC
          SESSION_SECRET: $SERVICE_PASSWORD_32_SESSION
          ENCRYPTION_KEY: $SERVICE_PASSWORD_32_ENCRYPTION
          PROVIDER_SECRET: $SERVICE_PASSWORD_64_PROVIDER
          COORDINATOR_SECRET: $SERVICE_PASSWORD_64_COORDINATOR
          DATABASE_HOST: 'postgresql:5432'
          DATABASE_URL: 'postgres://$SERVICE_USER_POSTGRES:$SERVICE_PASSWORD_POSTGRES@postgresql:5432/$POSTGRES_DB?sslmode=disable'
          DIRECT_URL: 'postgres://$SERVICE_USER_POSTGRES:$SERVICE_PASSWORD_POSTGRES@postgresql:5432/$POSTGRES_DB?sslmode=disable'
          REDIS_HOST: redis
          REDIS_PORT: 6379
          REDIS_TLS_DISABLED: true
          COORDINATOR_HOST: 127.0.0.1
          COORDINATOR_PORT: 9020
          WHITELISTED_EMAILS: ''
          ADMIN_EMAILS: ''
          DEFAULT_ORG_EXECUTION_CONCURRENCY_LIMIT: 300
          DEFAULT_ENV_EXECUTION_CONCURRENCY_LIMIT: 100
          DEPLOY_REGISTRY_HOST: docker.io
          DEPLOY_REGISTRY_NAMESPACE: trigger
          REGISTRY_HOST: '${DEPLOY_REGISTRY_HOST}'
          REGISTRY_NAMESPACE: '${DEPLOY_REGISTRY_NAMESPACE}'
          AUTH_GITHUB_CLIENT_ID: '${AUTH_GITHUB_CLIENT_ID}'
          AUTH_GITHUB_CLIENT_SECRET: '${AUTH_GITHUB_CLIENT_SECRET}'
          RESEND_API_KEY: '${RESEND_API_KEY}'
          FROM_EMAIL: '${FROM_EMAIL}'
          REPLY_TO_EMAIL: '${REPLY_TO_EMAIL}'
          LOGIN_ORIGIN: $SERVICE_URL_TRIGGER_3000
          APP_ORIGIN: $SERVICE_URL_TRIGGER_3000
          DEV_OTEL_EXPORTER_OTLP_ENDPOINT: $SERVICE_URL_TRIGGER_3000/otel
          OTEL_EXPORTER_OTLP_ENDPOINT: $SERVICE_URL_TRIGGER_3000/otel
          ELECTRIC_ORIGIN: 'http://electric:3000'
        depends_on:
          postgresql:
            condition: service_healthy
        healthcheck:
          test:
            - CMD-SHELL
            - pwd
      redis:
        image: 'redis:7'
        environment:
          - ALLOW_EMPTY_PASSWORD=yes
        healthcheck:
          test:
            - CMD-SHELL
            - 'redis-cli -h localhost -p 6379 ping'
          interval: 5s
          timeout: 5s
          retries: 3
        volumes:
          - 'redis-data:/data'
      postgresql:
        image: 'postgres:16-alpine'
        volumes:
          - 'postgresql-data:/var/lib/postgresql/data'
        environment:
          REMIX_APP_PORT: 3000
          NODE_ENV: production
          RUNTIME_PLATFORM: docker-compose
          V3_ENABLED: true
          INTERNAL_OTEL_TRACE_DISABLED: 1
          INTERNAL_OTEL_TRACE_LOGGING_ENABLED: 0
          POSTGRES_USER: $SERVICE_USER_POSTGRES
          POSTGRES_PASSWORD: $SERVICE_PASSWORD_POSTGRES
          POSTGRES_DB: '${POSTGRES_DB:-trigger}'
          MAGIC_LINK_SECRET: $SERVICE_PASSWORD_32_MAGIC
          SESSION_SECRET: $SERVICE_PASSWORD_32_SESSION
          ENCRYPTION_KEY: $SERVICE_PASSWORD_32_ENCRYPTION
          PROVIDER_SECRET: $SERVICE_PASSWORD_64_PROVIDER
          COORDINATOR_SECRET: $SERVICE_PASSWORD_64_COORDINATOR
          DATABASE_HOST: 'postgresql:5432'
          DATABASE_URL: 'postgres://$SERVICE_USER_POSTGRES:$SERVICE_PASSWORD_POSTGRES@postgresql:5432/$POSTGRES_DB?sslmode=disable'
          DIRECT_URL: 'postgres://$SERVICE_USER_POSTGRES:$SERVICE_PASSWORD_POSTGRES@postgresql:5432/$POSTGRES_DB?sslmode=disable'
          REDIS_HOST: redis
          REDIS_PORT: 6379
          REDIS_TLS_DISABLED: true
          COORDINATOR_HOST: 127.0.0.1
          COORDINATOR_PORT: 9020
          WHITELISTED_EMAILS: ''
          ADMIN_EMAILS: ''
          DEFAULT_ORG_EXECUTION_CONCURRENCY_LIMIT: 300
          DEFAULT_ENV_EXECUTION_CONCURRENCY_LIMIT: 100
          DEPLOY_REGISTRY_HOST: docker.io
          DEPLOY_REGISTRY_NAMESPACE: trigger
          REGISTRY_HOST: '${DEPLOY_REGISTRY_HOST}'
          REGISTRY_NAMESPACE: '${DEPLOY_REGISTRY_NAMESPACE}'
          AUTH_GITHUB_CLIENT_ID: '${AUTH_GITHUB_CLIENT_ID}'
          AUTH_GITHUB_CLIENT_SECRET: '${AUTH_GITHUB_CLIENT_SECRET}'
          RESEND_API_KEY: '${RESEND_API_KEY}'
          FROM_EMAIL: '${FROM_EMAIL}'
          REPLY_TO_EMAIL: '${REPLY_TO_EMAIL}'
          LOGIN_ORIGIN: $SERVICE_URL_TRIGGER_3000
          APP_ORIGIN: $SERVICE_URL_TRIGGER_3000
          DEV_OTEL_EXPORTER_OTLP_ENDPOINT: $SERVICE_URL_TRIGGER_3000/otel
          OTEL_EXPORTER_OTLP_ENDPOINT: $SERVICE_URL_TRIGGER_3000/otel
          ELECTRIC_ORIGIN: 'http://electric:3000'
        command:
          - '-c'
          - wal_level=logical
        healthcheck:
          test:
            - CMD-SHELL
            - 'pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}'
          interval: 5s
          timeout: 20s
          retries: 10
      docker-provider:
        image: 'ghcr.io/triggerdotdev/provider/docker:v3'
        platform: linux/amd64
        volumes:
          - '/var/run/docker.sock:/var/run/docker.sock'
        user: root
        depends_on:
          trigger:
            condition: service_healthy
        environment:
          REMIX_APP_PORT: 3000
          NODE_ENV: production
          RUNTIME_PLATFORM: docker-compose
          V3_ENABLED: true
          INTERNAL_OTEL_TRACE_DISABLED: 1
          INTERNAL_OTEL_TRACE_LOGGING_ENABLED: 0
          POSTGRES_USER: $SERVICE_USER_POSTGRES
          POSTGRES_PASSWORD: $SERVICE_PASSWORD_POSTGRES
          POSTGRES_DB: '${POSTGRES_DB:-trigger}'
          MAGIC_LINK_SECRET: $SERVICE_PASSWORD_32_MAGIC
          SESSION_SECRET: $SERVICE_PASSWORD_32_SESSION
          ENCRYPTION_KEY: $SERVICE_PASSWORD_32_ENCRYPTION
          PROVIDER_SECRET: $SERVICE_PASSWORD_64_PROVIDER
          COORDINATOR_SECRET: $SERVICE_PASSWORD_64_COORDINATOR
          DATABASE_HOST: 'postgresql:5432'
          DATABASE_URL: 'postgres://$SERVICE_USER_POSTGRES:$SERVICE_PASSWORD_POSTGRES@postgresql:5432/$POSTGRES_DB?sslmode=disable'
          DIRECT_URL: 'postgres://$SERVICE_USER_POSTGRES:$SERVICE_PASSWORD_POSTGRES@postgresql:5432/$POSTGRES_DB?sslmode=disable'
          REDIS_HOST: redis
          REDIS_PORT: 6379
          REDIS_TLS_DISABLED: true
          COORDINATOR_HOST: 127.0.0.1
          COORDINATOR_PORT: 9020
          WHITELISTED_EMAILS: ''
          ADMIN_EMAILS: ''
          DEFAULT_ORG_EXECUTION_CONCURRENCY_LIMIT: 300
          DEFAULT_ENV_EXECUTION_CONCURRENCY_LIMIT: 100
          DEPLOY_REGISTRY_HOST: docker.io
          DEPLOY_REGISTRY_NAMESPACE: trigger
          REGISTRY_HOST: '${DEPLOY_REGISTRY_HOST}'
          REGISTRY_NAMESPACE: '${DEPLOY_REGISTRY_NAMESPACE}'
          AUTH_GITHUB_CLIENT_ID: '${AUTH_GITHUB_CLIENT_ID}'
          AUTH_GITHUB_CLIENT_SECRET: '${AUTH_GITHUB_CLIENT_SECRET}'
          RESEND_API_KEY: '${RESEND_API_KEY}'
          FROM_EMAIL: '${FROM_EMAIL}'
          REPLY_TO_EMAIL: '${REPLY_TO_EMAIL}'
          LOGIN_ORIGIN: $SERVICE_URL_TRIGGER_3000
          APP_ORIGIN: $SERVICE_URL_TRIGGER_3000
          DEV_OTEL_EXPORTER_OTLP_ENDPOINT: $SERVICE_URL_TRIGGER_3000/otel
          OTEL_EXPORTER_OTLP_ENDPOINT: $SERVICE_URL_TRIGGER_3000/otel
          ELECTRIC_ORIGIN: 'http://electric:3000'
          PLATFORM_HOST: trigger
          PLATFORM_WS_PORT: 3000
          SECURE_CONNECTION: 'false'
          PLATFORM_SECRET: $SERVICE_PASSWORD_64_PROVIDER
          HTTP_SERVER_PORT: 9020
      coordinator:
        image: 'ghcr.io/triggerdotdev/coordinator:v3'
        platform: linux/amd64
        volumes:
          - '/var/run/docker.sock:/var/run/docker.sock'
        user: root
        ports:
          - '127.0.0.1:9020:9020'
        depends_on:
          trigger:
            condition: service_healthy
        environment:
          REMIX_APP_PORT: 3000
          NODE_ENV: production
          RUNTIME_PLATFORM: docker-compose
          V3_ENABLED: true
          INTERNAL_OTEL_TRACE_DISABLED: 1
          INTERNAL_OTEL_TRACE_LOGGING_ENABLED: 0
          POSTGRES_USER: $SERVICE_USER_POSTGRES
          POSTGRES_PASSWORD: $SERVICE_PASSWORD_POSTGRES
          POSTGRES_DB: '${POSTGRES_DB:-trigger}'
          MAGIC_LINK_SECRET: $SERVICE_PASSWORD_32_MAGIC
          SESSION_SECRET: $SERVICE_PASSWORD_32_SESSION
          ENCRYPTION_KEY: $SERVICE_PASSWORD_32_ENCRYPTION
          PROVIDER_SECRET: $SERVICE_PASSWORD_64_PROVIDER
          COORDINATOR_SECRET: $SERVICE_PASSWORD_64_COORDINATOR
          DATABASE_HOST: 'postgresql:5432'
          DATABASE_URL: 'postgres://$SERVICE_USER_POSTGRES:$SERVICE_PASSWORD_POSTGRES@postgresql:5432/$POSTGRES_DB?sslmode=disable'
          DIRECT_URL: 'postgres://$SERVICE_USER_POSTGRES:$SERVICE_PASSWORD_POSTGRES@postgresql:5432/$POSTGRES_DB?sslmode=disable'
          REDIS_HOST: redis
          REDIS_PORT: 6379
          REDIS_TLS_DISABLED: true
          COORDINATOR_HOST: 127.0.0.1
          COORDINATOR_PORT: 9020
          WHITELISTED_EMAILS: ''
          ADMIN_EMAILS: ''
          DEFAULT_ORG_EXECUTION_CONCURRENCY_LIMIT: 300
          DEFAULT_ENV_EXECUTION_CONCURRENCY_LIMIT: 100
          DEPLOY_REGISTRY_HOST: docker.io
          DEPLOY_REGISTRY_NAMESPACE: trigger
          REGISTRY_HOST: '${DEPLOY_REGISTRY_HOST}'
          REGISTRY_NAMESPACE: '${DEPLOY_REGISTRY_NAMESPACE}'
          AUTH_GITHUB_CLIENT_ID: '${AUTH_GITHUB_CLIENT_ID}'
          AUTH_GITHUB_CLIENT_SECRET: '${AUTH_GITHUB_CLIENT_SECRET}'
          RESEND_API_KEY: '${RESEND_API_KEY}'
          FROM_EMAIL: '${FROM_EMAIL}'
          REPLY_TO_EMAIL: '${REPLY_TO_EMAIL}'
          LOGIN_ORIGIN: $SERVICE_URL_TRIGGER_3000
          APP_ORIGIN: $SERVICE_URL_TRIGGER_3000
          DEV_OTEL_EXPORTER_OTLP_ENDPOINT: $SERVICE_URL_TRIGGER_3000/otel
          OTEL_EXPORTER_OTLP_ENDPOINT: $SERVICE_URL_TRIGGER_3000/otel
          ELECTRIC_ORIGIN: 'http://electric:3000'
          PLATFORM_HOST: trigger
          PLATFORM_WS_PORT: 3000
          SECURE_CONNECTION: 'false'
          PLATFORM_SECRET: $SERVICE_PASSWORD_64_COORDINATOR
          HTTP_SERVER_PORT: 9020
        healthcheck:
          test:
            - CMD-SHELL
            - pwd

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
2. Check Coolify documentation for trigger
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=trigger
   ```
