.PHONY: help install-deps update-deps setup-native start-agent dev-login prod-login dev-deploy prod-deploy dev-uninstall prod-uninstall dev-reinstall prod-reinstall dev-backup prod-backup dev-restore prod-restore lint test build-ansible clean \
	dev-docker-deploy prod-docker-deploy docker-test docker-lint \
	sync-apps dev-test-install-config \
	dev-create-app prod-create-app dev-restore-app prod-restore-app dev-uninstall-app prod-uninstall-app \
	dev-create-service prod-create-service dev-restore-service prod-restore-service dev-uninstall-service prod-uninstall-service \
	dev-create-db prod-create-db dev-restore-db prod-restore-db dev-uninstall-db prod-uninstall-db

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
	@echo ""
	@echo "Resource Management (dev/prod):"
	@echo "  {dev,prod}-create-{app,service,db}"
	@echo "  {dev,prod}-restore-{app,service,db}"
	@echo "  {dev,prod}-uninstall-{app,service,db}"
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
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify_create.yml $(EXTRA_VARS)

prod-deploy:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify_create.yml $(EXTRA_VARS)

dev-uninstall:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify_uninstall.yml $(EXTRA_VARS)

prod-uninstall:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify_uninstall.yml $(EXTRA_VARS)

dev-reinstall:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify_reinstall.yml $(EXTRA_VARS)

prod-reinstall:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify_reinstall.yml $(EXTRA_VARS)

dev-backup:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify_backup.yml $(EXTRA_VARS)

prod-backup:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify_backup.yml $(EXTRA_VARS)

dev-restore:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify_restore.yml $(EXTRA_VARS)

prod-restore:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify_restore.yml $(EXTRA_VARS)

sync-apps:
	cd ansible && ansible-playbook -i inventory/inventory.yml playbooks/coolify_application_sync.yml $(EXTRA_VARS)

# --- Resource Management ---

dev-create-app:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify_application_create.yml $(EXTRA_VARS)
prod-create-app:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify_application_create.yml $(EXTRA_VARS)
dev-restore-app:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify_application_restore.yml $(EXTRA_VARS)
prod-restore-app:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify_application_restore.yml $(EXTRA_VARS)
dev-uninstall-app:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify_application_uninstall.yml $(EXTRA_VARS)
prod-uninstall-app:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify_application_uninstall.yml $(EXTRA_VARS)

dev-create-service:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify_service_create.yml $(EXTRA_VARS)
prod-create-service:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify_service_create.yml $(EXTRA_VARS)
dev-restore-service:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify_service_restore.yml $(EXTRA_VARS)
prod-restore-service:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify_service_restore.yml $(EXTRA_VARS)
dev-uninstall-service:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify_service_uninstall.yml $(EXTRA_VARS)
prod-uninstall-service:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify_service_uninstall.yml $(EXTRA_VARS)

dev-create-db:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify_database_create.yml $(EXTRA_VARS)
prod-create-db:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify_database_create.yml $(EXTRA_VARS)
dev-restore-db:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify_database_restore.yml $(EXTRA_VARS)
prod-restore-db:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify_database_restore.yml $(EXTRA_VARS)
dev-uninstall-db:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify_database_uninstall.yml $(EXTRA_VARS)
prod-uninstall-db:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/coolify_database_uninstall.yml $(EXTRA_VARS)

lint:
	ansible-lint ansible/

test:
	cd ansible && ansible-playbook -i inventory/inventory.yml tests/test_parallels_vm.yml $(EXTRA_VARS)

# --- Configuration Tests ---

dev-test-install-config:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/coolify_create.yml \
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
	docker run $(DOCKER_RUN_ARGS) $(ANSIBLE_IMAGE) ansible-playbook -l development playbooks/coolify_create.yml

prod-docker-deploy:
	docker run $(DOCKER_RUN_ARGS) $(ANSIBLE_IMAGE) ansible-playbook -l production playbooks/coolify_create.yml

docker-test:
	docker run $(DOCKER_RUN_ARGS) $(ANSIBLE_IMAGE) ansible-playbook tests/test_parallels_vm.yml

docker-lint:
	docker run $(DOCKER_RUN_ARGS) $(ANSIBLE_IMAGE) ansible-lint .

# --- General ---

clean:
	find . -type f -name "*.retry" -delete
	rm -f ansible/.env .env
