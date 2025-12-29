# Coolify Service Compatibility

Auto-generated from service tests on 2025-12-29

## Summary

| Category | Tested | Passed | Failed | Pass Rate |
|----------|--------|--------|--------|-----------|
| Standalone | 48 | 33 | 15 | 68.8% |
| MariaDB | 11 | 10 | 1 | 90.9% |
| PostgreSQL | 27 | 18 | 9 | 66.7% |
| **Total** | **86** | **61** | **25** | **70.9%** |

## Standalone Services (No Database)

| Service | Status | Template | Notes |
|---------|--------|----------|-------|
| activepieces | :white_check_mark: | [templates/activepieces/](../templates/activepieces/) | - |
| appsmith | :white_check_mark: | [templates/appsmith/](../templates/appsmith/) | - |
| appwrite | :white_check_mark: | [templates/appwrite/](../templates/appwrite/) | - |
| authentik | :white_check_mark: | [templates/authentik/](../templates/authentik/) | - |
| babybuddy | :white_check_mark: | [templates/babybuddy/](../templates/babybuddy/) | - |
| budge | :white_check_mark: | [templates/budge/](../templates/budge/) | - |
| changedetection | :white_check_mark: | [templates/changedetection/](../templates/changedetection/) | - |
| classicpress-without-database | :white_check_mark: | [templates/classicpress-without-database/](../templates/classicpress-without-database/) | - |
| code-server | :white_check_mark: | [templates/code-server/](../templates/code-server/) | - |
| docker-registry | :white_check_mark: | [templates/docker-registry/](../templates/docker-registry/) | - |
| docuseal | :white_check_mark: | [templates/docuseal/](../templates/docuseal/) | - |
| docuseal-with-postgres | :white_check_mark: | [templates/docuseal-with-postgres/](../templates/docuseal-with-postgres/) | - |
| dokuwiki | :white_check_mark: | [templates/dokuwiki/](../templates/dokuwiki/) | - |
| duplicati | :white_check_mark: | [templates/duplicati/](../templates/duplicati/) | - |
| emby | :white_check_mark: | [templates/emby/](../templates/emby/) | - |
| embystat | :white_check_mark: | [templates/embystat/](../templates/embystat/) | - |
| filebrowser | :white_check_mark: | [templates/filebrowser/](../templates/filebrowser/) | - |
| glance | :white_check_mark: | [templates/glance/](../templates/glance/) | - |
| glances | :white_check_mark: | [templates/glances/](../templates/glances/) | - |
| grocy | :white_check_mark: | [templates/grocy/](../templates/grocy/) | - |
| heimdall | :white_check_mark: | [templates/heimdall/](../templates/heimdall/) | - |
| homepage | :white_check_mark: | [templates/homepage/](../templates/homepage/) | - |
| pairdrop | :white_check_mark: | [templates/pairdrop/](../templates/pairdrop/) | - |
| phpmyadmin | :white_check_mark: | [templates/phpmyadmin/](../templates/phpmyadmin/) | - |
| pocketbase | :white_check_mark: | [templates/pocketbase/](../templates/pocketbase/) | - |
| slash | :white_check_mark: | [templates/slash/](../templates/slash/) | - |
| snapdrop | :white_check_mark: | [templates/snapdrop/](../templates/snapdrop/) | - |
| statusnook | :white_check_mark: | [templates/statusnook/](../templates/statusnook/) | - |
| syncthing | :white_check_mark: | [templates/syncthing/](../templates/syncthing/) | - |
| uptime-kuma | :white_check_mark: | [templates/uptime-kuma/](../templates/uptime-kuma/) | - |
| vaultwarden | :white_check_mark: | [templates/vaultwarden/](../templates/vaultwarden/) | - |
| vikunja | :white_check_mark: | [templates/vikunja/](../templates/vikunja/) | - |
| whoogle | :white_check_mark: | [templates/whoogle/](../templates/whoogle/) | - |
| cloudflared | :x: | - | [See report](plan/service/cloudflared.md) |
| dashboard | :x: | - | [See report](plan/service/dashboard.md) |
| jellyfin | :x: | - | [See report](plan/service/jellyfin.md) |
| kuzzle | :x: | - | [See report](plan/service/kuzzle.md) |
| metube | :x: | - | [See report](plan/service/metube.md) |
| openblocks | :x: | - | [See report](plan/service/openblocks.md) |
| reactive-resume | :x: | - | [See report](plan/service/reactive-resume.md) |
| rocketchat | :x: | - | [See report](plan/service/rocketchat.md) |
| shlink | :x: | - | [See report](plan/service/shlink.md) |
| stirling-pdf | :x: | - | [See report](plan/service/stirling-pdf.md) |
| tolgee | :x: | - | [See report](plan/service/tolgee.md) |
| unleash-without-database | :x: | - | [See report](plan/service/unleash-without-database.md) |
| weblate | :x: | - | [See report](plan/service/weblate.md) |

## MariaDB Services

| Service | Status | Template | Notes |
|---------|--------|----------|-------|
| classicpress-with-mariadb | :white_check_mark: | [templates/classicpress-with-mariadb/](../templates/classicpress-with-mariadb/) | - |
| classicpress-with-mysql | :white_check_mark: | [templates/classicpress-with-mysql/](../templates/classicpress-with-mysql/) | - |
| firefly | :white_check_mark: | [templates/firefly/](../templates/firefly/) | - |
| ghost | :white_check_mark: | [templates/ghost/](../templates/ghost/) | - |
| gitea-with-mariadb | :white_check_mark: | [templates/gitea-with-mariadb/](../templates/gitea-with-mariadb/) | - |
| mediawiki | :white_check_mark: | [templates/mediawiki/](../templates/mediawiki/) | - |
| moodle | :white_check_mark: | [templates/moodle/](../templates/moodle/) | - |
| nextcloud | :white_check_mark: | [templates/nextcloud/](../templates/nextcloud/) | - |
| wordpress-with-mariadb | :white_check_mark: | [templates/wordpress-with-mariadb/](../templates/wordpress-with-mariadb/) | - |
| wordpress-with-mysql | :white_check_mark: | [templates/wordpress-with-mysql/](../templates/wordpress-with-mysql/) | - |
| gitea-with-mysql | :x: | - | [See report](plan/service/gitea-with-mysql.md) |

## PostgreSQL Services

| Service | Status | Template | Notes |
|---------|--------|----------|-------|
| chatwoot | :white_check_mark: | [templates/chatwoot/](../templates/chatwoot/) | - |
| directus | :white_check_mark: | [templates/directus/](../templates/directus/) | - |
| directus-with-postgresql | :white_check_mark: | [templates/directus-with-postgresql/](../templates/directus-with-postgresql/) | - |
| fider | :white_check_mark: | [templates/fider/](../templates/fider/) | - |
| formbricks | :white_check_mark: | [templates/formbricks/](../templates/formbricks/) | - |
| glitchtip | :white_check_mark: | [templates/glitchtip/](../templates/glitchtip/) | - |
| grafana | :white_check_mark: | [templates/grafana/](../templates/grafana/) | - |
| grafana-with-postgresql | :white_check_mark: | [templates/grafana-with-postgresql/](../templates/grafana-with-postgresql/) | - |
| logto | :white_check_mark: | [templates/logto/](../templates/logto/) | - |
| meilisearch | :white_check_mark: | [templates/meilisearch/](../templates/meilisearch/) | - |
| metabase | :white_check_mark: | [templates/metabase/](../templates/metabase/) | - |
| n8n | :white_check_mark: | [templates/n8n/](../templates/n8n/) | - |
| n8n-with-postgresql | :white_check_mark: | [templates/n8n-with-postgresql/](../templates/n8n-with-postgresql/) | - |
| nocodb | :white_check_mark: | [templates/nocodb/](../templates/nocodb/) | - |
| odoo | :white_check_mark: | [templates/odoo/](../templates/odoo/) | - |
| penpot | :white_check_mark: | [templates/penpot/](../templates/penpot/) | - |
| supabase | :white_check_mark: | [templates/supabase/](../templates/supabase/) | - |
| umami | :white_check_mark: | [templates/umami/](../templates/umami/) | - |
| gitea | :x: | - | [See report](plan/service/gitea.md) |
| gitea-with-postgresql | :x: | - | [See report](plan/service/gitea-with-postgresql.md) |
| listmonk | :x: | - | [See report](plan/service/listmonk.md) |
| minio | :x: | - | [See report](plan/service/minio.md) |
| posthog | :x: | - | [See report](plan/service/posthog.md) |
| trigger | :x: | - | [See report](plan/service/trigger.md) |
| trigger-with-external-database | :x: | - | [See report](plan/service/trigger-with-external-database.md) |
| twenty | :x: | - | [See report](plan/service/twenty.md) |
| unleash-with-postgresql | :x: | - | [See report](plan/service/unleash-with-postgresql.md) |

## Legend

- :white_check_mark: - Service tested successfully, template available
- :x: - Service failed testing, see report for details

## Re-testing

```bash
# Test a single service
make dev-test-service SERVICE=<service-name>

# Test all services in a category
make dev-test-standalone
make dev-test-mariadb
make dev-test-postgresql

# Test all services
make dev-test-all-services
```
