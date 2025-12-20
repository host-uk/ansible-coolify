.PHONY: help install-deps update-deps setup-native start-agent dev-login prod-login dev-deploy prod-deploy dev-uninstall prod-uninstall dev-reinstall prod-reinstall dev-backup prod-backup dev-restore prod-restore lint test build-ansible clean \
	dev-docker-deploy prod-docker-deploy docker-test docker-lint \
	sync-apps dev-test-install-config \
	dev-create-app prod-create-app dev-restore-app prod-restore-app dev-uninstall-app prod-uninstall-app \
	dev-create-service prod-create-service dev-restore-service prod-restore-service dev-uninstall-service prod-uninstall-service \
	dev-create-db prod-create-db dev-restore-db prod-restore-db dev-uninstall-db prod-uninstall-db \
	dev-clone-env-pb prod-clone-env-pb clone-env dev-clone-env clone-app-de-eu dev-clone-app-de-eu clone-host-uk-lon dev-clone-host-uk-lon \
	dev-empty-env-pb prod-empty-env-pb empty-env dev-empty-env clear-host-uk-lon dev-clear-host-uk-lon \
	dev-sync-apps

# Variables
ANSIBLE_IMAGE = ansible-coolify
DOCKER_RUN_ARGS = -it --rm \
	-v $(PWD)/ansible/inventory/inventory.yml:/config/inventory.yml \
	-v $(HOME)/.ssh/id_rsa:/secrets/ssh_key \
	-v $(HOME)/.ssh/id_rsa.pub:/secrets/ssh_key.pub \
	-v $(PWD)/ansible:/ansible

# Default target
help:
	@echo "Available targets (Native):"
	@echo "  setup-native       - Install native dependencies (brew/pip) and collections"
	@echo "  start-agent        - Ensure ssh-agent is running"
	@echo "  dev-login          - Add development SSH key to ssh-agent"
	@echo "  prod-login         - Add production SSH key to ssh-agent"
	@echo "  install-deps       - Install missing Ansible collections"
	@echo "  update-deps        - Force update all Ansible collections"
	@echo "  dev-deploy         - Run deployment for dev (native)"
	@echo "  prod-deploy        - Run deployment for prod (native)"
	@echo "  dev-backup         - Backup Coolify for dev (native)"
	@echo "  prod-backup        - Backup Coolify for prod (native)"
	@echo "  dev-restore        - Restore Coolify for dev (native)"
	@echo "  prod-restore       - Restore Coolify for prod (native)"
	@echo "  dev-uninstall      - Uninstall Coolify from dev (native)"
	@echo "  prod-uninstall     - Uninstall Coolify from prod (native)"
	@echo "  dev-reinstall      - Full reinstall for dev (Backup -> Uninstall -> Install -> Restore)"
	@echo "  prod-reinstall     - Full reinstall for prod (Backup -> Uninstall -> Install -> Restore)"
	@echo "  test               - Run Parallels VM lifecycle test (native)"
	@echo "  lint               - Run ansible-lint (native)"
	@echo ""
	@echo "  sync-apps          - Sync applications from development to production"
	@echo "  dev-sync-apps      - Sync applications from production to development"
	@echo ""
	@echo "Resource Management (dev/prod):"
	@echo "  {dev,prod}-create-{app,service,db}"
	@echo "  {dev,prod}-restore-{app,service,db}"
	@echo "  {dev,prod}-uninstall-{app,service,db}"
	@echo "  clone-env          - Clone environment (prod by default, requires SOURCE and TARGET)"
	@echo "  dev-clone-env      - Clone environment in dev (requires SOURCE and TARGET)"
	@echo "  clone-host-uk-lon  - Specific clone for host.uk.com (de -> lon, prod by default)"
	@echo "  dev-clone-host-uk-lon - Specific clone for host.uk.com in dev (de -> lon)"
	@echo "  empty-env          - Empty an environment (delete all resources, prod by default)"
	@echo "  dev-empty-env      - Empty an environment in dev (delete all resources)"
	@echo "  clear-host-uk-lon  - Specific clear for host.uk.com (lon, prod by default)"
	@echo "  dev-clear-host-uk-lon - Specific clear for host.uk.com in dev (lon)"
	@echo ""
	@echo "Available targets (Docker):"
	@echo "  build-ansible      - Build the Ansible Docker image"
	@echo "  dev-docker-deploy  - Run deployment for dev (docker)"
	@echo "  prod-docker-deploy - Run deployment for prod (docker)"
	@echo "  docker-test        - Run Parallels VM lifecycle test (docker)"
	@echo "  docker-lint        - Run ansible-lint (docker)"
	@echo ""
	@echo "Configuration Tests:"
	@echo "  dev-test-install-config - Test Coolify installation with custom config"
	@echo ""
	@echo "General:"
	@echo "  clean              - Clean up temporary files"
	@echo ""
	@echo "Examples:"
	@echo "  # Deploy to development with custom admin credentials"
	@echo "  make dev-deploy EXTRA_VARS=\"-e coolify_root_username=admin -e coolify_root_user_email=admin@example.com -e coolify_root_user_password=SecurePassword123!\""
	@echo ""
	@echo "  # Run only the parallels_vm setup"
	@echo "  make dev-deploy EXTRA_VARS=\"--tags parallels_vm\""
	@echo ""
	@echo "  # Uninstall Coolify"
	@echo "  make dev-uninstall"
	@echo ""
	@echo "  # Full reinstall (uninstall then deploy)"
	@echo "  make dev-uninstall && make dev-deploy"
	@echo ""
	@echo "  # Automated reinstall with Backup & Restore"
	@echo "  make dev-reinstall"

# --- Native Targets ---

setup-native:
	@if command -v brew >/dev/null 2>&1; then \
		brew install ansible ansible-lint jq yq; \
	else \
		echo "Homebrew not found, skipping brew install"; \
	fi
	pip install --upgrade pip
	pip install ansible-core distlib netaddr jsonschema ipaddr jmespath
	$(MAKE) install-deps

dev-login:
	@if ! pgrep -u $$USER ssh-agent > /dev/null; then \
		eval $$(ssh-agent -s) && ssh-add ~/.ssh/vm-worker; \
	else \
		ssh-add ~/.ssh/vm-worker; \
	fi

prod-login:
	@if ! pgrep -u $$USER ssh-agent > /dev/null; then \
		eval $$(ssh-agent -s) && ssh-add ~/.ssh/hostuk; \
	else \
		ssh-add ~/.ssh/hostuk; \
	fi

start-agent:
	@if ! pgrep -u $$USER ssh-agent > /dev/null; then \
		echo "Starting ssh-agent..."; \
		ssh-agent -s > ~/.ssh/ssh-agent.env; \
		echo "Agent started. Run 'source ~/.ssh/ssh-agent.env' to use it in your current shell."; \
	else \
		echo "ssh-agent is already running."; \
	fi

install-deps:
	cd ansible && ansible-galaxy collection install -r requirements.yml -p ./collections

update-deps:
	cd ansible && ansible-galaxy collection install -r requirements.yml -p ./collections --force

dev-deploy:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/create.yml $(EXTRA_VARS)

prod-deploy:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/create.yml $(EXTRA_VARS)

dev-uninstall:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/uninstall.yml $(EXTRA_VARS)

prod-uninstall:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/uninstall.yml $(EXTRA_VARS)

dev-reinstall:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/reinstall.yml $(EXTRA_VARS)

prod-reinstall:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/reinstall.yml $(EXTRA_VARS)

dev-backup:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/backup.yml $(EXTRA_VARS)

prod-backup:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/backup.yml $(EXTRA_VARS)

dev-restore:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/restore.yml $(EXTRA_VARS)

prod-restore:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/restore.yml $(EXTRA_VARS)

sync-apps:
	cd ansible && ansible-playbook -i inventory/inventory.yml playbooks/coolify/application/sync.yml \
		-e "coolify_source_controller=vm-controller" \
		-e "coolify_target_controller=noc.host.uk.com" \
		$(EXTRA_VARS)

dev-sync-apps:
	cd ansible && ansible-playbook -i inventory/inventory.yml playbooks/coolify/application/sync.yml \
		-e "coolify_source_controller=noc.host.uk.com" \
		-e "coolify_target_controller=vm-controller" \
		$(EXTRA_VARS)

# --- Resource Management ---

dev-create-app:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/application/create.yml $(EXTRA_VARS)
prod-create-app:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/application/create.yml $(EXTRA_VARS)
dev-restore-app:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/application/restore.yml $(EXTRA_VARS)
prod-restore-app:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/application/restore.yml $(EXTRA_VARS)
dev-uninstall-app:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/application/uninstall.yml $(EXTRA_VARS)
prod-uninstall-app:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/application/uninstall.yml $(EXTRA_VARS)

dev-create-service:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/service/create.yml $(EXTRA_VARS)
prod-create-service:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/service/create.yml $(EXTRA_VARS)
dev-restore-service:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/service/restore.yml $(EXTRA_VARS)
prod-restore-service:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/service/restore.yml $(EXTRA_VARS)
dev-uninstall-service:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/service/uninstall.yml $(EXTRA_VARS)
prod-uninstall-service:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/service/uninstall.yml $(EXTRA_VARS)

dev-create-db:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/database/create.yml $(EXTRA_VARS)
prod-create-db:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/database/create.yml $(EXTRA_VARS)
dev-restore-db:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/database/restore.yml $(EXTRA_VARS)
prod-restore-db:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/database/restore.yml $(EXTRA_VARS)
dev-uninstall-db:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/database/uninstall.yml $(EXTRA_VARS)
prod-uninstall-db:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/database/uninstall.yml $(EXTRA_VARS)

dev-clone-env-pb:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/environment/clone.yml $(EXTRA_VARS)
prod-clone-env-pb:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/environment/clone.yml $(EXTRA_VARS)

# Helper for dev cloning
dev-clone-env:
	@if [ -z "$(SOURCE)" ] || [ -z "$(TARGET)" ]; then \
		echo "Error: SOURCE and TARGET are required."; \
		echo "Usage: make dev-clone-env SOURCE=<source_env_name> TARGET=<target_env_name> [PROJECT=<project_uuid>]"; \
		exit 1; \
	fi
	$(MAKE) dev-clone-env-pb EXTRA_VARS="-e coolify_source_env_name=$(SOURCE) -e coolify_target_env_name=$(TARGET) $(if $(PROJECT),-e coolify_project_uuid=$(PROJECT))"

# Example: make clone-env SOURCE=app-de-eu-1.host.uk.com TARGET=app-de-eu-2.host.uk.com
clone-env:
	@if [ -z "$(SOURCE)" ] || [ -z "$(TARGET)" ]; then \
		echo "Error: SOURCE and TARGET are required."; \
		echo "Usage: make clone-env SOURCE=<source_env_name> TARGET=<target_env_name> [PROJECT=<project_uuid>]"; \
		exit 1; \
	fi
	$(MAKE) prod-clone-env-pb EXTRA_VARS="-e coolify_source_env_name=$(SOURCE) -e coolify_target_env_name=$(TARGET) $(if $(PROJECT),-e coolify_project_uuid=$(PROJECT))"

# Specific example for app-de-eu
clone-app-de-eu:
	$(MAKE) clone-env SOURCE=app-de-eu-1.host.uk.com TARGET=app-de-eu-2.host.uk.com PROJECT=eo0swss44080ssggkwgwocwg

dev-clone-app-de-eu:
	$(MAKE) dev-clone-env SOURCE=app-de-eu-1.host.uk.com TARGET=app-de-eu-2.host.uk.com PROJECT=eo0swss44080ssggkwgwocwg

# Clone for host.uk.com project: de -> lon
clone-host-uk-lon:
	$(MAKE) clone-env SOURCE=de.host.uk.com TARGET=lon.host.uk.com PROJECT=host.uk.com

dev-clone-host-uk-lon:
	$(MAKE) dev-clone-env SOURCE=de.host.uk.com TARGET=lon.host.uk.com PROJECT=host.uk.com

dev-empty-env-pb:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/environment/empty.yml $(EXTRA_VARS)
prod-empty-env-pb:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify/environment/empty.yml $(EXTRA_VARS)

empty-env:
	@if [ -z "$(ENV)" ] || [ -z "$(PROJECT)" ]; then \
		echo "Error: ENV and PROJECT are required."; \
		echo "Usage: make empty-env ENV=<env_name> PROJECT=<project_name_or_uuid>"; \
		exit 1; \
	fi
	$(MAKE) prod-empty-env-pb EXTRA_VARS="-e coolify_env_name=$(ENV) -e coolify_project_uuid=$(PROJECT)"

dev-empty-env:
	@if [ -z "$(ENV)" ] || [ -z "$(PROJECT)" ]; then \
		echo "Error: ENV and PROJECT are required."; \
		echo "Usage: make dev-empty-env ENV=<env_name> PROJECT=<project_name_or_uuid>"; \
		exit 1; \
	fi
	$(MAKE) dev-empty-env-pb EXTRA_VARS="-e coolify_env_name=$(ENV) -e coolify_project_uuid=$(PROJECT)"

clear-host-uk-lon:
	$(MAKE) empty-env ENV=lon.host.uk.com PROJECT=host.uk.com

dev-clear-host-uk-lon:
	$(MAKE) dev-empty-env ENV=lon.host.uk.com PROJECT=host.uk.com

lint:
	cd ansible && ansible-lint playbooks/ roles/

test: test-syntax test-logic test-parallels

test-syntax:
	cd ansible && ansible-playbook --syntax-check tests/test_coolify_roles_syntax.yml

test-logic:
	cd ansible && ansible-playbook tests/test_coolify_token.yml

test-parallels:
	cd ansible && ansible-playbook -i inventory/inventory.yml tests/test_parallels_vm.yml $(EXTRA_VARS)

# --- Configuration Tests ---

dev-test-install-config:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify/create.yml \
		-e "coolify_root_username=test" \
		-e "coolify_root_user_email=test@host.uk.com" \
		-e "coolify_root_user_password=Tesn735dfsd!" \
		-e "coolify_autoupdate=false" \
		$(EXTRA_VARS)


# --- Docker Targets ---

build-ansible:
	./ansible/scripts/docker_tag.sh
	cd ansible && docker build -t $(ANSIBLE_IMAGE) .

dev-docker-deploy:
	docker run $(DOCKER_RUN_ARGS) $(ANSIBLE_IMAGE) ansible-playbook -l development playbooks/coolify/create.yml

prod-docker-deploy:
	docker run $(DOCKER_RUN_ARGS) $(ANSIBLE_IMAGE) ansible-playbook -l production playbooks/coolify/create.yml

docker-test:
	docker run $(DOCKER_RUN_ARGS) $(ANSIBLE_IMAGE) /bin/sh -c "cd /ansible && ansible-playbook tests/test_coolify_token.yml && ansible-playbook tests/test_parallels_vm.yml"

docker-lint:
	docker run $(DOCKER_RUN_ARGS) $(ANSIBLE_IMAGE) /bin/sh -c "cd /ansible && ansible-lint playbooks/ roles/"

# --- General ---

clean:
	find . -type f -name "*.retry" -delete
	rm -f ansible/.env .env
