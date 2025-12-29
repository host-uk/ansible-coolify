# unleash-without-database - Test Failed

## Status: FAILED
## Tested: 2025-12-29T06:51:24+00:00
## Coolify Version: Unknown

## Error Summary

Service status is 'unknown' (not running/healthy)

## Container Logs

```
Logs not available
```

## Configuration Attempted

```yaml
service_type: unleash-without-database
project: service-tests
environment: testing
server_uuid: p8sw4ssksg4ksgg848kos8w4
service_uuid: xw88ss88okw8ogsoow8gokk8
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
2. Check Coolify documentation for unleash-without-database
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=unleash-without-database
   ```
