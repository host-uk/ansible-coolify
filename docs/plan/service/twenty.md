# twenty - Test Failed

## Status: FAILED
## Tested: 2025-12-29T08:44:05+00:00
## Coolify Version: Unknown

## Error Summary

Failed to create service: Status code was 400 and not [200, 201]: HTTP Error 400: Bad Request

## Container Logs

```

```

## Configuration Attempted

```yaml
service_type: twenty
project: service-tests
environment: testing
server_uuid: sswcwc404c4gskcsgkoockkc
service_uuid: 
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
2. Check Coolify documentation for twenty
3. Try deploying manually in Coolify UI to see detailed errors
4. Update `database_mappings.yml` if service has database requirements
5. Re-run test after fixes:
   ```bash
   make dev-test-service SERVICE=twenty
   ```
