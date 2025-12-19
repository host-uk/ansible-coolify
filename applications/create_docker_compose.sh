#!/bin/bash

# Simple script to create a Docker Compose application via Ansible
# Usage: ./create_docker_compose.sh <name> <project_uuid> <server_uuid> <docker_compose_file>

NAME=$1
PROJECT_UUID=$2
SERVER_UUID=$3
COMPOSE_FILE=$4

if [ -z "$NAME" ] || [ -z "$PROJECT_UUID" ] || [ -z "$SERVER_UUID" ] || [ -z "$COMPOSE_FILE" ]; then
    echo "Usage: $0 <name> <project_uuid> <server_uuid> <docker_compose_file>"
    exit 1
fi

COMPOSE_RAW=$(cat "$COMPOSE_FILE")

cd ../ansible
ansible-playbook -i inventory/inventory.yml -l development -e "{
  'coolify_application_type': 'dockercompose',
  'coolify_application_name': '$NAME',
  'coolify_application_project_uuid': '$PROJECT_UUID',
  'coolify_application_server_uuid': '$SERVER_UUID',
  'coolify_application_docker_compose_raw': \"$COMPOSE_RAW\"
}" playbooks/coolify_application_create.yml
