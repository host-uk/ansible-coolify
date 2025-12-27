#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Coolify Collection
# EUPL-1.2 License

"""
Ansible module for managing Coolify services.

This is a self-contained module that includes the HTTP client directly
to avoid module_utils import issues with role-based modules.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: coolify_service
short_description: Manage Coolify services
description:
    - Create, update, delete, and control services in Coolify.
    - Supports 90+ one-click services or custom Docker Compose.
    - Provides idempotent service management.
version_added: "1.0.0"
author:
    - Ansible Coolify Collection
options:
    api_url:
        description: Coolify API base URL
        type: str
        required: true
    api_token:
        description: Coolify API Bearer token
        type: str
        required: true
    state:
        description: Desired state of the service
        type: str
        choices: ['present', 'absent', 'started', 'stopped', 'restarted']
        default: present
    uuid:
        description: Service UUID (for updates/deletes)
        type: str
    name:
        description: Service name (required for creation)
        type: str
    service_type:
        description: |
            One-click service type or 'custom' for docker-compose.
            See Coolify documentation for full list of 90+ services.
        type: str
    project_uuid:
        description: UUID of the project where the service will be created
        type: str
    server_uuid:
        description: UUID of the server where the service will run
        type: str
    environment_name:
        description: Name of the environment (alternative to environment_uuid)
        type: str
    environment_uuid:
        description: UUID of the environment (alternative to environment_name)
        type: str
    description:
        description: Service description
        type: str
    docker_compose_raw:
        description: Docker Compose content (for custom services)
        type: str
    instant_deploy:
        description: Deploy immediately after creation
        type: bool
        default: false
    connect_to_docker_network:
        description: Connect to predefined Docker network
        type: bool
        default: false
    delete_configurations:
        description: Delete configurations when removing service
        type: bool
        default: true
    delete_volumes:
        description: Delete volumes when removing service
        type: bool
        default: true
    timeout:
        description: Request timeout in seconds
        type: int
        default: 30
    verify_ssl:
        description: Whether to verify SSL certificates
        type: bool
        default: true
'''

EXAMPLES = r'''
- name: Create a one-click Grafana service
  coolify_service:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: present
    name: "monitoring-grafana"
    service_type: "grafana"
    project_uuid: "{{ project_uuid }}"
    server_uuid: "{{ server_uuid }}"
    environment_name: "production"
    instant_deploy: true

- name: Create Uptime Kuma for monitoring
  coolify_service:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: present
    name: "uptime-monitor"
    service_type: "uptime-kuma"
    project_uuid: "{{ project_uuid }}"
    server_uuid: "{{ server_uuid }}"
    environment_name: "production"

- name: Create custom service from Docker Compose
  coolify_service:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: present
    name: "custom-app"
    project_uuid: "{{ project_uuid }}"
    server_uuid: "{{ server_uuid }}"
    environment_name: "production"
    docker_compose_raw: |
      version: '3.8'
      services:
        web:
          image: nginx:alpine
          ports:
            - "80:80"

- name: Start a service
  coolify_service:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: started
    uuid: "{{ service_uuid }}"

- name: Delete a service
  coolify_service:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: absent
    uuid: "{{ service_uuid }}"
'''

RETURN = r'''
service:
    description: The service details
    type: dict
    returned: when state is present
uuid:
    description: The service UUID
    type: str
    returned: when service exists
'''

import json
import ssl
import urllib.request
import urllib.error

from ansible.module_utils.basic import AnsibleModule

# List of known one-click service types
ONE_CLICK_SERVICES = [
    'activepieces', 'appsmith', 'appwrite', 'authentik', 'babybuddy',
    'budge', 'changedetection', 'chatwoot', 'classicpress-with-mariadb',
    'classicpress-with-mysql', 'classicpress-without-database', 'cloudflared',
    'code-server', 'dashboard', 'directus', 'directus-with-postgresql',
    'docker-registry', 'docmost', 'docuseal', 'docuseal-with-postgres',
    'dokuwiki', 'duplicati', 'emby', 'emby-stat', 'fider', 'filebrowser',
    'firefly', 'formbricks', 'ghost', 'gitea', 'gitea-with-mariadb',
    'gitea-with-mysql', 'gitea-with-postgresql', 'glances', 'glitchtip',
    'grafana', 'grafana-with-postgresql', 'grocy', 'heimdall', 'homepage',
    'jellyfin', 'kuzzle', 'langfuse', 'listmonk', 'logto', 'meilisearch',
    'metabase', 'metube', 'minio', 'moodle', 'n8n', 'n8n-with-postgresql',
    'nextcloud', 'nocodb', 'odoo', 'openblocks', 'pairdrop', 'penpot',
    'phpmyadmin', 'pocketbase', 'posthog', 'reactive-resume', 'rocketchat',
    'searxng', 'shlink', 'slash', 'statusnook', 'stirling-pdf', 'supabase',
    'trigger', 'trigger-with-external-database', 'twenty', 'umami',
    'unleash-with-postgresql', 'unleash-without-database', 'uptime-kuma',
    'vaultwarden', 'vikunja', 'weblate', 'whoogle', 'wordpress-with-mariadb',
    'wordpress-with-mysql', 'wordpress-without-database',
]


class CoolifyClient:
    """Minimal Coolify API client for service operations."""

    def __init__(self, base_url, api_token, timeout=30, verify_ssl=True):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    def _request(self, method, endpoint, data=None):
        """Make an HTTP request to the Coolify API."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        body = None
        if data:
            body = json.dumps(data).encode('utf-8')

        request = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            context = None
            if not self.verify_ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(request, timeout=self.timeout, context=context) as response:
                response_body = response.read().decode('utf-8')
                if response_body:
                    return json.loads(response_body)
                return {}

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ''
            try:
                error_data = json.loads(error_body)
                raise Exception(f"API error ({e.code}): {error_data.get('message', error_body)}")
            except json.JSONDecodeError:
                raise Exception(f"API error ({e.code}): {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Connection error: {e.reason}")

    def list_services(self):
        """List all services."""
        return self._request('GET', '/services')

    def get_service(self, uuid):
        """Get service by UUID."""
        return self._request('GET', f'/services/{uuid}')

    def create_service(self, **kwargs):
        """Create a new service."""
        # Filter out None values
        data = {k: v for k, v in kwargs.items() if v is not None}
        return self._request('POST', '/services', data)

    def update_service(self, uuid, **kwargs):
        """Update an existing service."""
        data = {k: v for k, v in kwargs.items() if v is not None}
        if data:
            return self._request('PATCH', f'/services/{uuid}', data)
        return None

    def delete_service(self, uuid, delete_configurations=True, delete_volumes=True):
        """Delete a service."""
        params = []
        if delete_configurations:
            params.append('delete_configurations=true')
        if delete_volumes:
            params.append('delete_volumes=true')
        query = '?' + '&'.join(params) if params else ''
        return self._request('DELETE', f'/services/{uuid}{query}')

    def start_service(self, uuid):
        """Start a service."""
        return self._request('POST', f'/services/{uuid}/start')

    def stop_service(self, uuid):
        """Stop a service."""
        return self._request('POST', f'/services/{uuid}/stop')

    def restart_service(self, uuid):
        """Restart a service."""
        return self._request('POST', f'/services/{uuid}/restart')


def find_service(client, name=None, uuid=None):
    """Find a service by name or UUID."""
    services = client.list_services()
    for svc in services:
        if uuid and svc.get('uuid') == uuid:
            return svc
        if name and svc.get('name') == name:
            return svc
    return None


def run_module():
    module_args = dict(
        api_url=dict(type='str', required=True),
        api_token=dict(type='str', required=True, no_log=True),
        state=dict(type='str', choices=['present', 'absent', 'started', 'stopped', 'restarted'], default='present'),
        uuid=dict(type='str'),
        name=dict(type='str'),
        service_type=dict(type='str'),
        project_uuid=dict(type='str'),
        server_uuid=dict(type='str'),
        environment_name=dict(type='str'),
        environment_uuid=dict(type='str'),
        description=dict(type='str'),
        docker_compose_raw=dict(type='str'),
        instant_deploy=dict(type='bool', default=False),
        connect_to_docker_network=dict(type='bool', default=False),
        delete_configurations=dict(type='bool', default=True),
        delete_volumes=dict(type='bool', default=True),
        timeout=dict(type='int', default=30),
        verify_ssl=dict(type='bool', default=True),
    )

    result = dict(
        changed=False,
        service=None,
        uuid=None,
        msg='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_one_of=[
            ['uuid', 'name'],
        ],
    )

    state = module.params['state']
    uuid = module.params['uuid']
    name = module.params['name']
    service_type = module.params['service_type']

    try:
        client = CoolifyClient(
            base_url=module.params['api_url'],
            api_token=module.params['api_token'],
            timeout=module.params['timeout'],
            verify_ssl=module.params['verify_ssl'],
        )

        # Find existing service
        existing = find_service(client, name=name, uuid=uuid)

        if state == 'present':
            if existing:
                result['service'] = existing
                result['uuid'] = existing['uuid']
                result['msg'] = f"Service '{name or uuid}' already exists"
            else:
                # Create new service
                if not module.params['project_uuid']:
                    module.fail_json(msg="project_uuid is required when creating a new service")
                if not module.params['server_uuid']:
                    module.fail_json(msg="server_uuid is required when creating a new service")
                if not name:
                    module.fail_json(msg="name is required when creating a new service")

                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = f"Would create service '{name}'"
                else:
                    create_params = {
                        'name': name,
                        'description': module.params['description'],
                        'project_uuid': module.params['project_uuid'],
                        'server_uuid': module.params['server_uuid'],
                        'environment_name': module.params['environment_name'],
                        'environment_uuid': module.params['environment_uuid'],
                        'instant_deploy': module.params['instant_deploy'],
                        'connect_to_docker_network': module.params['connect_to_docker_network'],
                    }

                    # Add type or docker_compose_raw
                    if service_type:
                        create_params['type'] = service_type
                    if module.params['docker_compose_raw']:
                        create_params['docker_compose_raw'] = module.params['docker_compose_raw']

                    svc = client.create_service(**create_params)
                    result['service'] = svc
                    result['uuid'] = svc.get('uuid')
                    result['changed'] = True
                    result['msg'] = f"Service '{name}' created"

        elif state == 'absent':
            if existing:
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = f"Would delete service '{name or uuid}'"
                else:
                    client.delete_service(
                        existing['uuid'],
                        delete_configurations=module.params['delete_configurations'],
                        delete_volumes=module.params['delete_volumes'],
                    )
                    result['changed'] = True
                    result['msg'] = f"Service '{name or uuid}' deleted"
            else:
                result['msg'] = f"Service '{name or uuid}' does not exist"

        elif state == 'started':
            if not existing:
                module.fail_json(msg=f"Service '{name or uuid}' not found")
            if module.check_mode:
                result['changed'] = True
                result['msg'] = f"Would start service '{name or uuid}'"
            else:
                client.start_service(existing['uuid'])
                result['service'] = existing
                result['uuid'] = existing['uuid']
                result['changed'] = True
                result['msg'] = f"Service '{name or uuid}' started"

        elif state == 'stopped':
            if not existing:
                module.fail_json(msg=f"Service '{name or uuid}' not found")
            if module.check_mode:
                result['changed'] = True
                result['msg'] = f"Would stop service '{name or uuid}'"
            else:
                client.stop_service(existing['uuid'])
                result['service'] = existing
                result['uuid'] = existing['uuid']
                result['changed'] = True
                result['msg'] = f"Service '{name or uuid}' stopped"

        elif state == 'restarted':
            if not existing:
                module.fail_json(msg=f"Service '{name or uuid}' not found")
            if module.check_mode:
                result['changed'] = True
                result['msg'] = f"Would restart service '{name or uuid}'"
            else:
                client.restart_service(existing['uuid'])
                result['service'] = existing
                result['uuid'] = existing['uuid']
                result['changed'] = True
                result['msg'] = f"Service '{name or uuid}' restarted"

    except Exception as e:
        result['msg'] = str(e)
        module.fail_json(**result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
