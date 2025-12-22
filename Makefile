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
	@echo "Examples:"
	@echo "  make dev-deploy EXTRA_VARS=\"-e coolify_root_username=admin ...\""

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

native-start-agent:
	@if ! pgrep -u $$USER ssh-agent > /dev/null; then \
		echo "Starting ssh-agent..."; \
		ssh-agent -s > ~/.ssh/ssh-agent.env; \
		echo "Agent started. Run 'source ~/.ssh/ssh-agent.env' to use it in your current shell."; \
	else \
		echo "ssh-agent is already running."; \
	fi

native-test: native-test-syntax native-test-logic native-test-parallels

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
	help \
	up down shell \
	native-build-ansible native-clean native-docker-lint native-docker-test native-install-deps native-lint \
	native-setup native-start-agent native-test native-test-logic native-test-parallels native-test-syntax native-update-deps \
	prod-backup prod-clear-host-uk-lon prod-clone-app-de-eu prod-clone-env prod-clone-env-pb prod-clone-host-uk-lon \
	prod-create-app prod-create-db prod-create-service prod-deploy prod-docker-deploy prod-empty-env prod-empty-env-pb \
	prod-hetzner-setup prod-login prod-reinstall prod-restore prod-restore-app prod-restore-db prod-restore-service \
	prod-sync-apps prod-uninstall prod-uninstall-app prod-uninstall-db prod-uninstall-service \
	_run-pb _run-docker
