.PHONY: help install-deps setup-native deploy-dev deploy-prod lint test build-ansible clean \
	docker-deploy-dev docker-deploy-prod docker-test docker-lint

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
	@echo "  install-deps       - Install Ansible collections only"
	@echo "  deploy-dev         - Run deployment for dev (native)"
	@echo "  deploy-prod        - Run deployment for prod (native)"
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
	@echo "General:"
	@echo "  clean              - Clean up temporary files"

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

install-deps:
	cd ansible && ansible-galaxy collection install -r requirements.yml -p ./collections --force

deploy-dev:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l development playbooks/playbook_install_coolify.yml

deploy-prod:
	cd ansible && ansible-playbook -i inventory/inventory.yml -l production playbooks/playbook_install_coolify.yml

lint:
	ansible-lint ansible/

test:
	cd ansible && ansible-playbook -i inventory/inventory.yml tests/test_parallels_vm.yml

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
