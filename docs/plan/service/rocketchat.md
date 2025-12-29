# rocketchat - Test Failed

## Status: FAILED
## Tested: 2025-12-29T05:31:55+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'exited' (not running/healthy)

## Container Logs

```
{'message': 'Not found.', 'docs': 'https://coolify.io/docs'}
```

## Configuration Attempted

```yaml
service_type: rocketchat
project: service-tests
environment: testing
server_uuid: p8sw4ssksg4ksgg848kos8w4
service_uuid: t8ggwogg48wok884k84gckcw
```

## Service Details from API

```yaml
status: exited
fqdn: Not set
docker_compose_raw: |
services:
      rocketchat:
        image: 'registry.rocket.chat/rocketchat/rocket.chat:latest'
        environment:
          - SERVICE_URL_ROCKETCHAT_3000
          - 'MONGO_URL=mongodb://${MONGODB_ADVERTISED_HOSTNAME:-mongodb}:${MONGODB_INITIAL_PRIMARY_PORT_NUMBER:-27017}/${MONGODB_DATABASE:-rocketchat}?replicaSet=${MONGODB_REPLICA_SET_NAME:-rs0}'
          - 'MONGO_OPLOG_URL=mongodb://${MONGODB_ADVERTISED_HOSTNAME:-mongodb}:${MONGODB_INITIAL_PRIMARY_PORT_NUMBER:-27017}/local?replicaSet=${MONGODB_REPLICA_SET_NAME:-rs0}'
          - ROOT_URL=$SERVICE_URL_ROCKETCHAT
          - DEPLOY_METHOD=docker
          - REG_TOKEN=$REG_TOKEN
        depends_on:
          mongodb:
            condition: service_healthy
        healthcheck:
          test:
            - CMD
            - node
            - '--eval'
            - "const http = require('http'); const options = { host: '0.0.0.0', port: 3000, timeout: 2000, path: '/health' }; const healthCheck = http.request(options, (res) => { console.log('HEALTHCHECK STATUS:', res.statusCode); if (res.statusCode == 200) { process.exit(0); } else { process.exit(1); } }); healthCheck.on('error', function (err) { console.error('ERROR'); process.exit(1); }); healthCheck.end();"
          interval: 2s
          timeout: 10s
          retries: 15
      mongodb:
        image: 'docker.io/bitnamilegacy/mongodb:5.0'
        volumes:
          - 'mongodb_data:/bitnami/mongodb'
        environment:
          - MONGODB_REPLICA_SET_MODE=primary
          - 'MONGODB_REPLICA_SET_NAME=${MONGODB_REPLICA_SET_NAME:-rs0}'
          - 'MONGODB_PORT_NUMBER=${MONGODB_PORT_NUMBER:-27017}'
          - 'MONGODB_INITIAL_PRIMARY_HOST=${MONGODB_INITIAL_PRIMARY_HOST:-mongodb}'
          - 'MONGODB_INITIAL_PRIMARY_PORT_NUMBER=${MONGODB_INITIAL_PRIMARY_PORT_NUMBER:-27017}'
          - 'MONGODB_ADVERTISED_HOSTNAME=${MONGODB_ADVERTISED_HOSTNAME:-mongodb}'
          - 'MONGODB_ENABLE_JOURNAL=${MONGODB_ENABLE_JOURNAL:-true}'
          - 'ALLOW_EMPTY_PASSWORD=${ALLOW_EMPTY_PASSWORD:-yes}'
        healthcheck:
          test: "echo 'db.stats().ok' | mongo localhost:27017/test --quiet"
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
2. Check Coolify documentation for rocketchat
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=rocketchat
   ```
