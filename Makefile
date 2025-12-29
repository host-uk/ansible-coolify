# Variables
ANSIBLE_IMAGE = ansible-coolify
DEV_CONTROLLER ?= controller.lan
PROD_CONTROLLER ?= controller.lan
DOCKER_RUN_ARGS = -it --rm \
	-v $(PWD):/ansible \
	-v $(HOME)/.ssh:/root/.ssh:ro \
	$(if $(SSH_AUTH_SOCK),-v $(SSH_AUTH_SOCK):/run/ssh-agent -e SSH_AUTH_SOCK=/run/ssh-agent)

.DEFAULT_GOAL := help

# --- Development Targets ---

dev-backup:
	$(MAKE) _run-pb PB=playbooks/coolify/backup.yml LIMIT=development

dev-clear-host-uk-lon:
	$(MAKE) dev-empty-env ENV=lon.example.com PROJECT=example.com

dev-clone-app-de-eu:
	$(MAKE) dev-clone-env SOURCE=app1.example.com TARGET=app2.example.com PROJECT=example-project-uuid

dev-clone-env:
	@if [ -z "$(SOURCE)" ] || [ -z "$(TARGET)" ]; then \
		echo "Error: SOURCE and TARGET are required."; \
		echo "Usage: make dev-clone-env SOURCE=<source_env_name> TARGET=<target_env_name> [PROJECT=<project_uuid>]"; \
		exit 1; \
	fi
	$(MAKE) dev-clone-env-pb VARS="-e coolify_source_env_name=$(SOURCE) -e coolify_target_env_name=$(TARGET) $(if $(PROJECT),-e coolify_project_uuid=$(PROJECT))"

dev-clone-env-pb:
	$(MAKE) _run-pb PB=playbooks/coolify/environment/clone.yml LIMIT=development

dev-clone-host-uk-lon:
	$(MAKE) dev-clone-env SOURCE=app1.example.com TARGET=app2.example.com PROJECT=example.com

dev-create-app:
	$(MAKE) _run-pb PB=playbooks/coolify/application/create.yml LIMIT=development

dev-create-db:
	$(MAKE) _run-pb PB=playbooks/coolify/database/create.yml LIMIT=development

dev-create-service:
	$(MAKE) _run-pb PB=playbooks/coolify/service/create.yml LIMIT=development

dev-configure-automation:
	$(MAKE) _run-pb PB=playbooks/coolify/configure_automation.yml LIMIT=development

dev-deploy:
	$(MAKE) _run-pb PB=playbooks/coolify/create.yml LIMIT=development

dev-docker-deploy:
	$(MAKE) _run-docker CMD="ansible-playbook -l development playbooks/coolify/create.yml"

dev-empty-env:
	@if [ -z "$(ENV)" ] || [ -z "$(PROJECT)" ]; then \
		echo "Error: ENV and PROJECT are required."; \
		echo "Usage: make dev-empty-env ENV=<env_name> PROJECT=<project_name_or_uuid>"; \
		exit 1; \
	fi
	$(MAKE) dev-empty-env-pb VARS="-e coolify_env_name=$(ENV) -e coolify_project_uuid=$(PROJECT)"

dev-empty-env-pb:
	$(MAKE) _run-pb PB=playbooks/coolify/environment/empty.yml LIMIT=development

dev-hetzner-setup:
	$(MAKE) _run-pb PB=playbooks/hetzner_setup.yml LIMIT=development

dev-login:
	@if ! pgrep -u $$USER ssh-agent > /dev/null; then \
		eval $$(ssh-agent -s) && ssh-add ~/.ssh/controller.lan ~/.ssh/app-server.lan ~/.ssh/builder.lan; \
	else \
		ssh-add ~/.ssh/controller.lan ~/.ssh/app-server.lan ~/.ssh/builder.lan; \
	fi

dev-reinstall:
	$(MAKE) _run-pb PB=playbooks/coolify/reinstall.yml LIMIT=development

dev-restore:
	$(MAKE) _run-pb PB=playbooks/coolify/restore.yml LIMIT=development

dev-restore-app:
	$(MAKE) _run-pb PB=playbooks/coolify/application/restore.yml LIMIT=development

dev-restore-db:
	$(MAKE) _run-pb PB=playbooks/coolify/database/restore.yml LIMIT=development

dev-restore-service:
	$(MAKE) _run-pb PB=playbooks/coolify/service/restore.yml LIMIT=development

dev-sync-apps:
	$(MAKE) _run-pb PB=playbooks/coolify/application/sync.yml \
		VARS="-e coolify_source_controller=$(PROD_CONTROLLER) -e coolify_target_controller=$(DEV_CONTROLLER)"

dev-test-install-config:
	$(MAKE) _run-pb PB=playbooks/coolify/create.yml LIMIT=development \
		VARS="-e coolify_root_username=root -e coolify_root_user_email=root@localhost -e coolify_root_user_password=Host.uk.com -e coolify_autoupdate=false"

dev-uninstall:
	$(MAKE) _run-pb PB=playbooks/coolify/uninstall.yml LIMIT=development

dev-uninstall-app:
	$(MAKE) _run-pb PB=playbooks/coolify/application/uninstall.yml LIMIT=development

dev-uninstall-db:
	$(MAKE) _run-pb PB=playbooks/coolify/database/uninstall.yml LIMIT=development

dev-uninstall-service:
	$(MAKE) _run-pb PB=playbooks/coolify/service/uninstall.yml LIMIT=development

# --- General ---

help:
	@echo "Available targets (Development):"
	@echo "  dev-backup         - Backup Coolify for dev"
	@echo "  dev-deploy         - Run deployment for dev"
	@echo "  dev-hetzner-setup  - Infrastructure discovery for dev"
	@echo "  dev-login          - Add development SSH key to ssh-agent"
	@echo "  dev-reinstall      - Full reinstall for dev"
	@echo "  dev-restore        - Restore Coolify for dev"
	@echo "  dev-sync-apps      - Sync applications from production to development"
	@echo "  dev-uninstall      - Uninstall Coolify from dev"
	@echo ""
	@echo "Available targets (Native):"
	@echo "  native-build-ansible - Build the Ansible Docker image"
	@echo "  native-clean       - Clean up temporary files"
	@echo "  native-install-deps - Install missing Ansible collections"
	@echo "  native-lint        - Run ansible-lint"
	@echo "  native-setup       - Install native dependencies and collections"
	@echo "  native-start-agent - Ensure ssh-agent is running"
	@echo "  native-test        - Run all tests"
	@echo "  native-update-deps - Force update all Ansible collections"
	@echo ""
	@echo "Available targets (Docker Compose):"
	@echo "  up                 - Start the Ansible container in the background"
	@echo "  down               - Stop and remove the Ansible container"
	@echo "  shell              - Open a shell in the running Ansible container"
	@echo ""
	@echo "Available targets (Docker Dev Environment):"
	@echo "  docker-dev-up      - Create and start Docker dev containers"
	@echo "  docker-dev-down    - Stop Docker dev containers"
	@echo "  docker-dev-destroy - Remove containers, volumes, and images"
	@echo "  docker-dev-logs    - Follow all container logs"
	@echo "  docker-dev-status  - Show container status"
	@echo "  docker-dev-shell-* - Shell into container (e.g., docker-dev-shell-controller)"
	@echo ""
	@echo "Available targets (Production):"
	@echo "  prod-backup        - Backup Coolify for prod"
	@echo "  prod-deploy        - Run deployment for prod"
	@echo "  prod-hetzner-setup - Infrastructure discovery for prod"
	@echo "  prod-login         - Add production SSH key to ssh-agent"
	@echo "  prod-reinstall     - Full reinstall for prod"
	@echo "  prod-restore       - Restore Coolify for prod"
	@echo "  prod-sync-apps     - Sync applications from development to production"
	@echo "  prod-uninstall     - Uninstall Coolify from prod"
	@echo ""
	@echo "Resource Management ({dev,prod}-*):"
	@echo "  create-{app,service,db}"
	@echo "  restore-{app,service,db}"
	@echo "  uninstall-{app,service,db}"
	@echo "  clone-env          - Clone environment (requires SOURCE and TARGET)"
	@echo "  empty-env          - Empty an environment (delete all resources)"
	@echo ""
	@echo "Available targets (Service Testing):"
	@echo "  dev-test-service   - Test a single service (SERVICE=name)"
	@echo "  dev-test-standalone - Test all standalone services"
	@echo "  dev-test-mariadb   - Test all MariaDB-based services"
	@echo "  dev-test-postgresql - Test all PostgreSQL-based services"
	@echo "  dev-test-all-services - Test all 100+ services"
	@echo "  dev-service-report - View service compatibility report"
	@echo ""
	@echo "Examples:"
	@echo "  make dev-deploy EXTRA_VARS=\"-e coolify_root_username=admin ...\""
	@echo "  make dev-test-service SERVICE=uptime-kuma"

# --- Native Targets ---

native-build-ansible:
	docker build -t $(ANSIBLE_IMAGE) .

native-clean:
	find . -type f -name "*.retry" -delete

native-docker-lint:
	$(MAKE) _run-docker CMD="/bin/sh -c 'ansible-lint playbooks/ roles/'"

native-docker-test:
	$(MAKE) _run-docker CMD="/bin/sh -c 'ansible-playbook tests/test_coolify_token.yml && ansible-playbook tests/test_parallels_vm.yml'"

native-install-deps:
	ansible-galaxy collection install -r requirements.yml -p ./collections

native-lint:
	ansible-lint playbooks/ roles/

native-setup:
	@if command -v brew >/dev/null 2>&1; then \
		brew install ansible ansible-lint jq yq; \
	else \
		echo "Homebrew not found, skipping brew install"; \
	fi
	pip install --upgrade pip
	pip install ansible-core distlib netaddr jsonschema ipaddr jmespath
	$(MAKE) native-install-deps
	@echo "Configuring git hooks..."
	git config core.hooksPath .githooks

native-start-agent:
	@if ! pgrep -u $$USER ssh-agent > /dev/null; then \
		echo "Starting ssh-agent..."; \
		ssh-agent -s > ~/.ssh/ssh-agent.env; \
		echo "Agent started. Run 'source ~/.ssh/ssh-agent.env' to use it in your current shell."; \
	else \
		echo "ssh-agent is already running."; \
	fi

native-test: native-test-syntax native-test-logic native-test-docker native-test-parallels

native-test-docker:
	$(MAKE) _run-pb PB=tests/test_docker_dev.yml

native-test-logic:
	$(MAKE) _run-pb PB=tests/test_coolify_token.yml

native-test-parallels:
	$(MAKE) _run-pb PB=tests/test_parallels_vm.yml

native-test-syntax:
	$(MAKE) _run-pb PB=tests/test_coolify_roles_syntax.yml FLAGS="--syntax-check"

native-test-token-extraction:
	$(MAKE) _run-pb PB=tests/test_coolify_token.yml

native-update-deps:
	ansible-galaxy collection install -r requirements.yml -p ./collections --force

# --- Docker Compose Targets ---

up:
	docker compose up -d --build

down:
	docker compose down

shell:
	docker compose exec ansible /bin/bash

# --- Docker Dev Environment Targets ---

DOCKER_DEV_COMPOSE = docker compose -f playbooks/coolify/docker-dev/docker-compose.yml

docker-dev-up:
	@echo "Starting Docker development containers..."
	ansible-playbook -i inventory/ playbooks/coolify/create.yml --tags docker_dev
	@echo ""
	@echo "Docker development environment is ready!"
	@echo "Run 'make docker-dev-logs' to follow container logs"
	@echo "Run 'make docker-dev-status' to check container status"

docker-dev-deploy:
	@echo "Deploying Coolify to Docker development environment..."
	$(MAKE) _run-pb PB=playbooks/coolify/create.yml LIMIT=development

docker-dev-down:
	$(DOCKER_DEV_COMPOSE) down

docker-dev-destroy:
	$(DOCKER_DEV_COMPOSE) down -v --rmi local
	rm -rf docker-dev-logs/

docker-dev-logs:
	$(DOCKER_DEV_COMPOSE) logs -f

docker-dev-logs-controller:
	$(DOCKER_DEV_COMPOSE) logs -f controller

docker-dev-logs-builder:
	$(DOCKER_DEV_COMPOSE) logs -f builder

docker-dev-shell-controller:
	docker exec -it coolify-dev-controller /bin/bash

docker-dev-shell-builder:
	docker exec -it coolify-dev-builder /bin/bash

docker-dev-shell-%:
	docker exec -it coolify-dev-$* /bin/bash

docker-dev-status:
	$(DOCKER_DEV_COMPOSE) ps

docker-dev-restart:
	$(DOCKER_DEV_COMPOSE) restart

# --- Docker Dev Test Targets ---

docker-dev-test: docker-dev-test-quick

docker-dev-test-quick:
	@echo "Running quick Docker dev tests (container, SSH, Makefile)..."
	bash tests/docker-dev/scripts/run_all_tests.sh quick

docker-dev-test-full:
	@echo "Running full Docker dev test suite..."
	bash tests/docker-dev/scripts/run_all_tests.sh full

docker-dev-test-api:
	@echo "Running API tests..."
	bash tests/docker-dev/scripts/run_all_tests.sh api

docker-dev-test-container:
	$(MAKE) _run-pb PB=tests/docker-dev/test_01_container_lifecycle.yml

docker-dev-test-ssh:
	$(MAKE) _run-pb PB=tests/docker-dev/test_02_ssh_connectivity.yml

docker-dev-test-makefile:
	$(MAKE) _run-pb PB=tests/docker-dev/test_03_makefile_targets.yml

docker-dev-test-install:
	$(MAKE) _run-pb PB=tests/docker-dev/test_04_coolify_install.yml

docker-dev-test-api-setup:
	$(MAKE) _run-pb PB=tests/docker-dev/test_05_api_setup.yml

docker-dev-test-node-registration:
	$(MAKE) _run-pb PB=tests/docker-dev/test_06_node_registration.yml

docker-dev-test-integration:
	$(MAKE) _run-pb PB=tests/docker-dev/test_07_full_integration.yml

docker-dev-cleanup:
	bash tests/docker-dev/scripts/cleanup.sh

# --- Galera Cluster Targets ---

dev-galera-deploy:
	$(MAKE) _run-pb PB=playbooks/coolify/galera/deploy.yml LIMIT=development

dev-galera-status:
	$(MAKE) _run-pb PB=playbooks/coolify/galera/status.yml LIMIT=development

dev-galera-status-wsrep:
	$(MAKE) _run-pb PB=playbooks/coolify/galera/status.yml LIMIT=development VARS="-e check_wsrep=true"

dev-galera-backup:
	$(MAKE) _run-pb PB=playbooks/coolify/galera/backup.yml LIMIT=development

dev-galera-restore:
	@if [ -z "$(BACKUP)" ]; then \
		echo "Error: BACKUP is required."; \
		echo "Usage: make dev-galera-restore BACKUP=<backup_filename>"; \
		echo "Available backups:"; \
		ls -la state/galera/backups/*.sql.gz 2>/dev/null || echo "  (none found)"; \
		exit 1; \
	fi
	$(MAKE) _run-pb PB=playbooks/coolify/galera/restore.yml LIMIT=development \
		VARS="-e backup_file=$(BACKUP) -e confirm_restore=true"

dev-galera-recover:
	@if [ -z "$(NODE)" ]; then \
		echo "Error: NODE is required."; \
		echo "Usage: make dev-galera-recover NODE=<hostname>"; \
		exit 1; \
	fi
	$(MAKE) _run-pb PB=playbooks/coolify/galera/recover.yml LIMIT=development \
		VARS="-e recover_node=$(NODE)"

dev-galera-test:
	@echo "Running Galera cluster tests..."
	$(MAKE) _run-pb PB=tests/docker-dev/test_08_galera_cluster.yml
	$(MAKE) _run-pb PB=tests/docker-dev/test_09_galera_failover.yml
	$(MAKE) _run-pb PB=tests/docker-dev/test_10_galera_backup.yml
	$(MAKE) _run-pb PB=tests/docker-dev/test_11_galera_laravel.yml

prod-galera-deploy:
	$(MAKE) _run-pb PB=playbooks/coolify/galera/deploy.yml LIMIT=production

prod-galera-status:
	$(MAKE) _run-pb PB=playbooks/coolify/galera/status.yml LIMIT=production

prod-galera-backup:
	$(MAKE) _run-pb PB=playbooks/coolify/galera/backup.yml LIMIT=production

prod-galera-restore:
	@if [ -z "$(BACKUP)" ]; then \
		echo "Error: BACKUP is required."; \
		echo "Usage: make prod-galera-restore BACKUP=<backup_filename>"; \
		exit 1; \
	fi
	$(MAKE) _run-pb PB=playbooks/coolify/galera/restore.yml LIMIT=production \
		VARS="-e backup_file=$(BACKUP) -e confirm_restore=true"

prod-galera-recover:
	@if [ -z "$(NODE)" ]; then \
		echo "Error: NODE is required."; \
		exit 1; \
	fi
	$(MAKE) _run-pb PB=playbooks/coolify/galera/recover.yml LIMIT=production \
		VARS="-e recover_node=$(NODE)"

# --- Redis Sentinel Cluster Targets ---

dev-redis-deploy:
	$(MAKE) _run-pb PB=playbooks/coolify/redis/deploy.yml LIMIT=development

dev-redis-status:
	$(MAKE) _run-pb PB=playbooks/coolify/redis/status.yml LIMIT=development

dev-redis-backup:
	$(MAKE) _run-pb PB=playbooks/coolify/redis/backup.yml LIMIT=development

dev-redis-failover:
	$(MAKE) _run-pb PB=playbooks/coolify/redis/failover.yml LIMIT=development

dev-redis-test:
	@echo "Running Redis Sentinel cluster tests..."
	$(MAKE) _run-pb PB=tests/docker-dev/test_15_redis_sentinel.yml

prod-redis-deploy:
	$(MAKE) _run-pb PB=playbooks/coolify/redis/deploy.yml LIMIT=production

prod-redis-status:
	$(MAKE) _run-pb PB=playbooks/coolify/redis/status.yml LIMIT=production

prod-redis-backup:
	$(MAKE) _run-pb PB=playbooks/coolify/redis/backup.yml LIMIT=production

prod-redis-failover:
	$(MAKE) _run-pb PB=playbooks/coolify/redis/failover.yml LIMIT=production

# --- PostgreSQL Patroni Cluster Targets ---

dev-postgresql-deploy:
	$(MAKE) _run-pb PB=playbooks/coolify/postgresql/deploy.yml LIMIT=development

dev-postgresql-status:
	$(MAKE) _run-pb PB=playbooks/coolify/postgresql/status.yml LIMIT=development

dev-postgresql-backup:
	$(MAKE) _run-pb PB=playbooks/coolify/postgresql/backup.yml LIMIT=development

dev-postgresql-switchover:
	$(MAKE) _run-pb PB=playbooks/coolify/postgresql/switchover.yml LIMIT=development

dev-postgresql-test:
	@echo "Running PostgreSQL Patroni cluster tests..."
	$(MAKE) _run-pb PB=tests/docker-dev/test_16_postgresql_patroni.yml

prod-postgresql-deploy:
	$(MAKE) _run-pb PB=playbooks/coolify/postgresql/deploy.yml LIMIT=production

prod-postgresql-status:
	$(MAKE) _run-pb PB=playbooks/coolify/postgresql/status.yml LIMIT=production

prod-postgresql-backup:
	$(MAKE) _run-pb PB=playbooks/coolify/postgresql/backup.yml LIMIT=production

prod-postgresql-switchover:
	$(MAKE) _run-pb PB=playbooks/coolify/postgresql/switchover.yml LIMIT=production

# --- Cluster Orchestration Targets ---

dev-cluster-deploy:
	@echo "Deploying complete shared infrastructure cluster..."
	$(MAKE) _run-pb PB=playbooks/coolify/cluster/deploy.yml LIMIT=development

dev-cluster-status:
	$(MAKE) _run-pb PB=playbooks/coolify/cluster/status.yml LIMIT=development

dev-cluster-backup:
	$(MAKE) _run-pb PB=playbooks/coolify/cluster/backup.yml LIMIT=development

dev-cluster-test:
	@echo "Running full cluster integration tests..."
	$(MAKE) _run-pb PB=tests/docker-dev/test_18_full_cluster.yml

prod-cluster-deploy:
	@echo "Deploying complete shared infrastructure cluster..."
	$(MAKE) _run-pb PB=playbooks/coolify/cluster/deploy.yml LIMIT=production

prod-cluster-status:
	$(MAKE) _run-pb PB=playbooks/coolify/cluster/status.yml LIMIT=production

prod-cluster-backup:
	$(MAKE) _run-pb PB=playbooks/coolify/cluster/backup.yml LIMIT=production

# --- One-Click App Targets ---

dev-oneclick-deploy:
	@if [ -z "$(APP)" ] || [ -z "$(NAME)" ]; then \
		echo "Error: APP and NAME are required."; \
		echo "Usage: make dev-oneclick-deploy APP=<service_type> NAME=<app_name>"; \
		echo "Examples:"; \
		echo "  make dev-oneclick-deploy APP=chatwoot NAME=my-chatwoot"; \
		echo "  make dev-oneclick-deploy APP=n8n NAME=automation"; \
		echo "  make dev-oneclick-deploy APP=uptime-kuma NAME=monitoring"; \
		exit 1; \
	fi
	$(MAKE) _run-pb PB=playbooks/coolify/oneclick/deploy.yml LIMIT=development \
		VARS="-e oneclick_service_type=$(APP) -e oneclick_app_name=$(NAME)"

dev-oneclick-list:
	$(MAKE) _run-pb PB=playbooks/coolify/oneclick/list.yml

dev-oneclick-detect:
	@if [ -z "$(APP)" ]; then \
		echo "Error: APP is required."; \
		echo "Usage: make dev-oneclick-detect APP=<service_type>"; \
		exit 1; \
	fi
	$(MAKE) _run-pb PB=playbooks/coolify/oneclick/detect.yml \
		VARS="-e oneclick_service_type=$(APP)"

dev-oneclick-test:
	@echo "Running One-Click App tests..."
	$(MAKE) _run-pb PB=tests/docker-dev/test_17_oneclick_app.yml

prod-oneclick-deploy:
	@if [ -z "$(APP)" ] || [ -z "$(NAME)" ]; then \
		echo "Error: APP and NAME are required."; \
		echo "Usage: make prod-oneclick-deploy APP=<service_type> NAME=<app_name>"; \
		exit 1; \
	fi
	$(MAKE) _run-pb PB=playbooks/coolify/oneclick/deploy.yml LIMIT=production \
		VARS="-e oneclick_service_type=$(APP) -e oneclick_app_name=$(NAME)"

prod-oneclick-list:
	$(MAKE) _run-pb PB=playbooks/coolify/oneclick/list.yml

prod-oneclick-detect:
	@if [ -z "$(APP)" ]; then \
		echo "Error: APP is required."; \
		exit 1; \
	fi
	$(MAKE) _run-pb PB=playbooks/coolify/oneclick/detect.yml \
		VARS="-e oneclick_service_type=$(APP)"

# --- Service Testing Targets ---
# These targets use tests/docker-dev/.env.test.local for API credentials
# Create from template: cp tests/docker-dev/.env.test tests/docker-dev/.env.test.local

# Helper to source env file if it exists
SERVICE_TEST_ENV := tests/docker-dev/.env.test.local
define source_test_env
	$(if $(wildcard $(SERVICE_TEST_ENV)),. $(SERVICE_TEST_ENV) &&,)
endef

dev-test-service:
	@if [ -z "$(SERVICE)" ]; then \
		echo "Error: SERVICE is required."; \
		echo "Usage: make dev-test-service SERVICE=<service_type>"; \
		echo "Example: make dev-test-service SERVICE=uptime-kuma"; \
		exit 1; \
	fi
	@if [ ! -f $(SERVICE_TEST_ENV) ]; then \
		echo "Warning: $(SERVICE_TEST_ENV) not found."; \
		echo "Create it: cp tests/docker-dev/.env.test $(SERVICE_TEST_ENV)"; \
		echo "Then set COOLIFY_API_TOKEN in the file."; \
	fi
	@$(source_test_env) $(MAKE) _run-pb PB=playbooks/coolify/service-test/test_service.yml \
		VARS="-e service_name=$(SERVICE)"

dev-test-standalone:
	@echo "Testing standalone services (no database dependencies)..."
	@$(source_test_env) $(MAKE) _run-pb PB=playbooks/coolify/service-test/test_all.yml \
		VARS="-e category=standalone"

dev-test-mariadb:
	@echo "Testing MariaDB-based services..."
	@$(source_test_env) $(MAKE) _run-pb PB=playbooks/coolify/service-test/test_all.yml \
		VARS="-e category=mariadb"

dev-test-postgresql:
	@echo "Testing PostgreSQL-based services..."
	@$(source_test_env) $(MAKE) _run-pb PB=playbooks/coolify/service-test/test_all.yml \
		VARS="-e category=postgresql"

dev-test-all-services:
	@echo "Testing all Coolify services..."
	@$(source_test_env) $(MAKE) _run-pb PB=playbooks/coolify/service-test/test_all.yml \
		VARS="-e category=all"

dev-service-report:
	@echo "Service compatibility report: docs/service_compatibility.md"
	@if [ -f docs/service_compatibility.md ]; then \
		cat docs/service_compatibility.md; \
	else \
		echo "No report found. Run 'make dev-test-all-services' first."; \
	fi

# --- API Verification Test Targets ---

native-test-api-verify:
	@echo "Running API verification tests..."
	$(MAKE) _run-pb PB=tests/docker-dev/test_12_api_verification.yml

native-test-service-verify:
	@echo "Running service verification tests..."
	$(MAKE) _run-pb PB=tests/docker-dev/test_13_service_verification.yml

native-test-chatwoot-galera:
	@echo "Running Chatwoot + Galera integration test..."
	$(MAKE) _run-pb PB=tests/docker-dev/test_14_chatwoot_galera.yml

native-test-redis-sentinel:
	@echo "Running Redis Sentinel cluster test..."
	$(MAKE) _run-pb PB=tests/docker-dev/test_15_redis_sentinel.yml

native-test-postgresql-patroni:
	@echo "Running PostgreSQL Patroni cluster test..."
	$(MAKE) _run-pb PB=tests/docker-dev/test_16_postgresql_patroni.yml

native-test-oneclick-app:
	@echo "Running One-Click App tests..."
	$(MAKE) _run-pb PB=tests/docker-dev/test_17_oneclick_app.yml

native-test-full-cluster:
	@echo "Running Full Cluster Integration tests..."
	$(MAKE) _run-pb PB=tests/docker-dev/test_18_full_cluster.yml

native-test-verify-all:
	@echo "Running all verification tests..."
	$(MAKE) native-test-api-verify
	$(MAKE) native-test-service-verify
	$(MAKE) native-test-chatwoot-galera
	$(MAKE) native-test-redis-sentinel
	$(MAKE) native-test-postgresql-patroni
	$(MAKE) native-test-oneclick-app
	$(MAKE) native-test-full-cluster

# --- Production Targets ---

prod-backup:
	$(MAKE) _run-pb PB=playbooks/coolify/backup.yml LIMIT=production

prod-clear-host-uk-lon:
	$(MAKE) prod-empty-env ENV=lon.example.com PROJECT=example.com

prod-clone-app-de-eu:
	$(MAKE) prod-clone-env SOURCE=app1.example.com TARGET=app2.example.com PROJECT=example-project-uuid

prod-clone-env:
	@if [ -z "$(SOURCE)" ] || [ -z "$(TARGET)" ]; then \
		echo "Error: SOURCE and TARGET are required."; \
		echo "Usage: make prod-clone-env SOURCE=<source_env_name> TARGET=<target_env_name> [PROJECT=<project_uuid>]"; \
		exit 1; \
	fi
	$(MAKE) prod-clone-env-pb VARS="-e coolify_source_env_name=$(SOURCE) -e coolify_target_env_name=$(TARGET) $(if $(PROJECT),-e coolify_project_uuid=$(PROJECT))"

prod-clone-env-pb:
	$(MAKE) _run-pb PB=playbooks/coolify/environment/clone.yml LIMIT=production

prod-clone-host-uk-lon:
	$(MAKE) prod-clone-env SOURCE=app1.example.com TARGET=app2.example.com PROJECT=example.com

prod-create-app:
	$(MAKE) _run-pb PB=playbooks/coolify/application/create.yml LIMIT=production

prod-create-db:
	$(MAKE) _run-pb PB=playbooks/coolify/database/create.yml LIMIT=production

prod-create-service:
	$(MAKE) _run-pb PB=playbooks/coolify/service/create.yml LIMIT=production

prod-configure-automation:
	$(MAKE) _run-pb PB=playbooks/coolify/configure_automation.yml LIMIT=production

prod-deploy:
	$(MAKE) _run-pb PB=playbooks/coolify/create.yml LIMIT=production

prod-docker-deploy:
	$(MAKE) _run-docker CMD="ansible-playbook -l production playbooks/coolify/create.yml"

prod-empty-env:
	@if [ -z "$(ENV)" ] || [ -z "$(PROJECT)" ]; then \
		echo "Error: ENV and PROJECT are required."; \
		echo "Usage: make prod-empty-env ENV=<env_name> PROJECT=<project_name_or_uuid>"; \
		exit 1; \
	fi
	$(MAKE) prod-empty-env-pb VARS="-e coolify_env_name=$(ENV) -e coolify_project_uuid=$(PROJECT)"

prod-empty-env-pb:
	$(MAKE) _run-pb PB=playbooks/coolify/environment/empty.yml LIMIT=production

prod-hetzner-setup:
	$(MAKE) _run-pb PB=playbooks/hetzner_setup.yml LIMIT=production

prod-login:
	@if ! pgrep -u $$USER ssh-agent > /dev/null; then \
		eval $$(ssh-agent -s) && ssh-add ~/.ssh/hostuk; \
	else \
		ssh-add ~/.ssh/hostuk; \
	fi

prod-reinstall:
	$(MAKE) _run-pb PB=playbooks/coolify/reinstall.yml LIMIT=production

prod-restore:
	$(MAKE) _run-pb PB=playbooks/coolify/restore.yml LIMIT=production

prod-restore-app:
	$(MAKE) _run-pb PB=playbooks/coolify/application/restore.yml LIMIT=production

prod-restore-db:
	$(MAKE) _run-pb PB=playbooks/coolify/database/restore.yml LIMIT=production

prod-restore-service:
	$(MAKE) _run-pb PB=playbooks/coolify/service/restore.yml LIMIT=production

prod-sync-apps:
	$(MAKE) _run-pb PB=playbooks/coolify/application/sync.yml \
		VARS="-e coolify_source_controller=$(DEV_CONTROLLER) -e coolify_target_controller=$(PROD_CONTROLLER)"

prod-uninstall:
	$(MAKE) _run-pb PB=playbooks/coolify/uninstall.yml LIMIT=production

prod-uninstall-app:
	$(MAKE) _run-pb PB=playbooks/coolify/application/uninstall.yml LIMIT=production

prod-uninstall-db:
	$(MAKE) _run-pb PB=playbooks/coolify/database/uninstall.yml LIMIT=production

prod-uninstall-service:
	$(MAKE) _run-pb PB=playbooks/coolify/service/uninstall.yml LIMIT=production

# --- Utilities (Internal) ---

# Run an ansible playbook
# Usage: $(MAKE) _run-pb PB=path/to/pb.yml [LIMIT=host_or_group] [VARS="key=val"] [FLAGS="--syntax-check"]
_run-pb:
	ansible-playbook -i inventory/ $(if $(LIMIT),-l $(LIMIT)) $(FLAGS) $(PB) $(VARS) $(EXTRA_VARS)

# Run a command inside the Ansible Docker container
# Usage: $(MAKE) _run-docker CMD="command"
_run-docker:
	docker run $(DOCKER_RUN_ARGS) $(ANSIBLE_IMAGE) $(CMD)

.PHONY: dev-backup dev-clear-host-uk-lon dev-clone-app-de-eu dev-clone-env dev-clone-env-pb dev-clone-host-uk-lon \
	dev-create-app dev-create-db dev-create-service dev-deploy dev-docker-deploy dev-empty-env dev-empty-env-pb \
	dev-hetzner-setup dev-login dev-reinstall dev-restore dev-restore-app dev-restore-db dev-restore-service \
	dev-sync-apps dev-test-install-config dev-uninstall dev-uninstall-app dev-uninstall-db dev-uninstall-service \
	dev-galera-deploy dev-galera-status dev-galera-status-wsrep dev-galera-backup dev-galera-restore dev-galera-recover dev-galera-test \
	help \
	up down shell \
	docker-dev-up docker-dev-down docker-dev-destroy docker-dev-logs docker-dev-logs-controller docker-dev-logs-builder \
	docker-dev-shell-controller docker-dev-shell-builder docker-dev-status docker-dev-restart \
	docker-dev-test docker-dev-test-quick docker-dev-test-full docker-dev-test-api \
	docker-dev-test-container docker-dev-test-ssh docker-dev-test-makefile docker-dev-test-install \
	docker-dev-test-api-setup docker-dev-test-node-registration docker-dev-test-integration docker-dev-cleanup \
	native-build-ansible native-clean native-docker-lint native-docker-test native-install-deps native-lint \
	native-setup native-start-agent native-test native-test-docker native-test-logic native-test-parallels native-test-syntax native-update-deps \
	native-test-api-verify native-test-service-verify native-test-chatwoot-galera native-test-redis-sentinel native-test-postgresql-patroni native-test-oneclick-app native-test-full-cluster native-test-verify-all \
	prod-backup prod-clear-host-uk-lon prod-clone-app-de-eu prod-clone-env prod-clone-env-pb prod-clone-host-uk-lon \
	prod-create-app prod-create-db prod-create-service prod-deploy prod-docker-deploy prod-empty-env prod-empty-env-pb \
	prod-hetzner-setup prod-login prod-reinstall prod-restore prod-restore-app prod-restore-db prod-restore-service \
	prod-sync-apps prod-uninstall prod-uninstall-app prod-uninstall-db prod-uninstall-service \
	prod-galera-deploy prod-galera-status prod-galera-backup prod-galera-restore prod-galera-recover \
	dev-redis-deploy dev-redis-status dev-redis-backup dev-redis-failover dev-redis-test \
	prod-redis-deploy prod-redis-status prod-redis-backup prod-redis-failover \
	dev-postgresql-deploy dev-postgresql-status dev-postgresql-backup dev-postgresql-switchover dev-postgresql-test \
	prod-postgresql-deploy prod-postgresql-status prod-postgresql-backup prod-postgresql-switchover \
	dev-oneclick-deploy dev-oneclick-list dev-oneclick-detect dev-oneclick-test \
	prod-oneclick-deploy prod-oneclick-list prod-oneclick-detect \
	dev-cluster-deploy dev-cluster-status dev-cluster-backup dev-cluster-test \
	prod-cluster-deploy prod-cluster-status prod-cluster-backup \
	dev-test-service dev-test-standalone dev-test-mariadb dev-test-postgresql dev-test-all-services dev-service-report \
	_run-pb _run-docker
