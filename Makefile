.PHONY: help install-deps update-deps setup-native start-agent login-dev login-prod deploy-dev deploy-prod lint test build-ansible clean \
	docker-deploy-dev docker-deploy-prod docker-test docker-lint \
	backup-dev backup-prod restore-dev restore-prod

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
	@echo "  login-dev          - Add development SSH key to ssh-agent"
	@echo "  login-prod         - Add production SSH key to ssh-agent"
	@echo "  install-deps       - Install missing Ansible collections"
	@echo "  update-deps        - Force update all Ansible collections"
	@echo "  deploy-dev         - Run deployment for dev (native)"
	@echo "  deploy-prod        - Run deployment for prod (native)"
	@echo "  backup-dev         - Backup Coolify for dev (native)"
	@echo "  backup-prod        - Backup Coolify for prod (native)"
	@echo "  restore-dev        - Restore Coolify for dev (native)"
	@echo "  restore-prod       - Restore Coolify for prod (native)"
	@echo "  uninstall-dev      - Uninstall Coolify from dev (native)"
	@echo "  uninstall-prod     - Uninstall Coolify from prod (native)"
	@echo "  reinstall-dev      - Full reinstall for dev (Backup -> Uninstall -> Install -> Restore)"
	@echo "  reinstall-prod     - Full reinstall for prod (Backup -> Uninstall -> Install -> Restore)"
	@echo "  test               - Run Parallels VM lifecycle test (native)"
	@echo "  lint               - Run ansible-lint (native)"
	@echo ""
	@echo "Available targets (Docker):"
	@echo "  build-ansible      - Build the Ansible Docker image"
	@echo "  docker-deploy-dev  - Run deployment for dev (docker)"
	@echo "  docker-deploy-prod - Run deployment for prod (docker)"
	@echo "  docker-test        - Run Parallels VM lifecycle test (docker)"
	@echo "  docker-lint        - Run ansible-lint (docker)"
	@echo ""
	@echo "Configuration Tests:"
	@echo "  test-coolify-install-config - Test Coolify installation with custom config"
	@echo ""
	@echo "General:"
	@echo "  clean              - Clean up temporary files"
	@echo ""
	@echo "Examples:"
	@echo "  # Deploy to development with custom admin credentials"
	@echo "  make deploy-dev EXTRA_VARS=\"-e coolify_root_username=admin -e coolify_root_user_email=admin@example.com -e coolify_root_user_password=SecurePassword123!\""
	@echo ""
	@echo "  # Run only the parallels_vm setup"
	@echo "  make deploy-dev EXTRA_VARS=\"--tags parallels_vm\""
	@echo ""
	@echo "  # Uninstall Coolify"
	@echo "  make uninstall-dev"
	@echo ""
	@echo "  # Full reinstall (uninstall then deploy)"
	@echo "  make uninstall-dev && make deploy-dev"
	@echo ""
	@echo "  # Automated reinstall with Backup & Restore"
	@echo "  make reinstall-dev"

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

login-dev:
	@if ! pgrep -u $$USER ssh-agent > /dev/null; then \
		eval $$(ssh-agent -s) && ssh-add ~/.ssh/vm-worker; \
	else \
		ssh-add ~/.ssh/vm-worker; \
	fi

login-prod:
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

deploy-dev:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/playbook_install_coolify.yml $(EXTRA_VARS)

deploy-prod:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/playbook_install_coolify.yml $(EXTRA_VARS)

uninstall-dev:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/playbook_uninstall_coolify.yml $(EXTRA_VARS)

uninstall-prod:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/playbook_uninstall_coolify.yml $(EXTRA_VARS)

reinstall-dev:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/playbook_reinstall_coolify.yml $(EXTRA_VARS)

reinstall-prod:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/playbook_reinstall_coolify.yml $(EXTRA_VARS)

backup-dev:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/playbook_backup_coolify.yml $(EXTRA_VARS)

backup-prod:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/playbook_backup_coolify.yml $(EXTRA_VARS)

restore-dev:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/playbook_restore_coolify.yml $(EXTRA_VARS)

restore-prod:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/playbook_restore_coolify.yml $(EXTRA_VARS)

lint:
	ansible-lint ansible/

test:
	cd ansible && ansible-playbook -i inventory/inventory.yml tests/test_parallels_vm.yml $(EXTRA_VARS)

# --- Configuration Tests ---

test-coolify-install-config:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/playbook_install_coolify.yml \
		-e "coolify_root_username=test" \
		-e "coolify_root_user_email=test@host.uk.com" \
		-e "coolify_root_user_password=Tesn735dfsd!" \
		-e "coolify_autoupdate=false" \
		$(EXTRA_VARS)


# --- Docker Targets ---

build-ansible:
	./ansible/scripts/docker_tag.sh
	cd ansible && docker build -t $(ANSIBLE_IMAGE) .

docker-deploy-dev:
	docker run $(DOCKER_RUN_ARGS) $(ANSIBLE_IMAGE) ansible-playbook -l development playbooks/playbook_install_coolify.yml

docker-deploy-prod:
	docker run $(DOCKER_RUN_ARGS) $(ANSIBLE_IMAGE) ansible-playbook -l production playbooks/playbook_install_coolify.yml

docker-test:
	docker run $(DOCKER_RUN_ARGS) $(ANSIBLE_IMAGE) ansible-playbook tests/test_parallels_vm.yml

docker-lint:
	docker run $(DOCKER_RUN_ARGS) $(ANSIBLE_IMAGE) ansible-lint .

# --- General ---

clean:
	find . -type f -name "*.retry" -delete
	rm -f ansible/.env .env
