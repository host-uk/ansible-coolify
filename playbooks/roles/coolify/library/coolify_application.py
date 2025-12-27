#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Coolify Collection
# EUPL-1.2 License

"""
Ansible module for managing Coolify applications.

This is a self-contained module that includes the HTTP client directly
to avoid module_utils import issues with role-based modules.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: coolify_application
short_description: Manage Coolify applications
description:
    - Create, update, delete, and control applications in Coolify.
    - Supports multiple application types (public, private, dockerfile, docker-image, docker-compose).
    - Provides idempotent application management.
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
        description: Desired state of the application
        type: str
        choices: ['present', 'absent', 'started', 'stopped', 'restarted', 'deployed']
        default: present
    uuid:
        description: Application UUID (for updates/deletes)
        type: str
    name:
        description: Application name
        type: str
    application_type:
        description: |
            Type of application to create.
            Required when creating a new application.
        type: str
        choices: ['public', 'private-github-app', 'private-deploy-key', 'dockerfile', 'dockerimage', 'dockercompose']
    project_uuid:
        description: UUID of the project where the application will be created
        type: str
    server_uuid:
        description: UUID of the server where the application will run
        type: str
    environment_name:
        description: Name of the environment (alternative to environment_uuid)
        type: str
    environment_uuid:
        description: UUID of the environment (alternative to environment_name)
        type: str
    description:
        description: Application description
        type: str
    git_repository:
        description: Git repository URL
        type: str
    git_branch:
        description: Git branch to deploy
        type: str
    build_pack:
        description: Build pack type
        type: str
        choices: ['nixpacks', 'static', 'dockerfile', 'dockercompose']
    ports_exposes:
        description: Ports to expose (comma-separated)
        type: str
    domains:
        description: Domain(s) for the application
        type: str
    dockerfile:
        description: Dockerfile content (for dockerfile type)
        type: str
    docker_registry_image_name:
        description: Docker image name (for dockerimage type)
        type: str
    docker_registry_image_tag:
        description: Docker image tag (for dockerimage type)
        type: str
    docker_compose_raw:
        description: Docker Compose content (for dockercompose type)
        type: str
    instant_deploy:
        description: Deploy immediately after creation
        type: bool
        default: false
    delete_configurations:
        description: Delete configurations when removing application
        type: bool
        default: true
    delete_volumes:
        description: Delete volumes when removing application
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
- name: Create application from public git repo
  coolify_application:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: present
    name: "my-web-app"
    application_type: public
    project_uuid: "{{ project_uuid }}"
    server_uuid: "{{ server_uuid }}"
    environment_name: "production"
    git_repository: "https://github.com/user/repo"
    git_branch: "main"
    build_pack: "nixpacks"
    ports_exposes: "3000"
    domains: "app.example.com"

- name: Create application from Docker image
  coolify_application:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: present
    name: "nginx-app"
    application_type: dockerimage
    project_uuid: "{{ project_uuid }}"
    server_uuid: "{{ server_uuid }}"
    environment_name: "production"
    docker_registry_image_name: "nginx"
    docker_registry_image_tag: "alpine"
    ports_exposes: "80"

- name: Start an application
  coolify_application:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: started
    uuid: "{{ app_uuid }}"

- name: Deploy an application
  coolify_application:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: deployed
    uuid: "{{ app_uuid }}"

- name: Delete an application
  coolify_application:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: absent
    uuid: "{{ app_uuid }}"
'''

RETURN = r'''
application:
    description: The application details
    type: dict
    returned: when state is present
uuid:
    description: The application UUID
    type: str
    returned: when application exists
deployment_uuid:
    description: UUID of triggered deployment
    type: str
    returned: when state is deployed
'''

import json
import ssl
import urllib.request
import urllib.error
import urllib.parse

from ansible.module_utils.basic import AnsibleModule


class CoolifyClient:
    """Minimal Coolify API client for application operations."""

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

    def list_applications(self):
        """List all applications."""
        return self._request('GET', '/applications')

    def get_application(self, uuid):
        """Get application by UUID."""
        return self._request('GET', f'/applications/{uuid}')

    def create_application(self, app_type, **kwargs):
        """Create a new application based on type."""
        type_endpoints = {
            'public': '/applications/public',
            'private-github-app': '/applications/private-github-app',
            'private-deploy-key': '/applications/private-deploy-key',
            'dockerfile': '/applications/dockerfile',
            'dockerimage': '/applications/dockerimage',
            'dockercompose': '/applications/dockercompose',
        }
        endpoint = type_endpoints.get(app_type)
        if not endpoint:
            raise Exception(f"Unknown application type: {app_type}")

        # Filter out None values
        data = {k: v for k, v in kwargs.items() if v is not None}
        return self._request('POST', endpoint, data)

    def update_application(self, uuid, **kwargs):
        """Update an existing application."""
        data = {k: v for k, v in kwargs.items() if v is not None}
        if data:
            return self._request('PATCH', f'/applications/{uuid}', data)
        return None

    def delete_application(self, uuid, delete_configurations=True, delete_volumes=True):
        """Delete an application."""
        params = []
        if delete_configurations:
            params.append('delete_configurations=true')
        if delete_volumes:
            params.append('delete_volumes=true')
        query = '?' + '&'.join(params) if params else ''
        return self._request('DELETE', f'/applications/{uuid}{query}')

    def start_application(self, uuid):
        """Start an application."""
        return self._request('POST', f'/applications/{uuid}/start')

    def stop_application(self, uuid):
        """Stop an application."""
        return self._request('POST', f'/applications/{uuid}/stop')

    def restart_application(self, uuid):
        """Restart an application."""
        return self._request('POST', f'/applications/{uuid}/restart')

    def deploy_application(self, uuid):
        """Trigger a deployment for the application."""
        # Using deploy endpoint with uuid parameter
        return self._request('POST', f'/deploy?uuid={uuid}')


def find_application(client, name=None, uuid=None, project_uuid=None, environment_name=None):
    """Find an application by name, UUID, or within a specific project/environment."""
    applications = client.list_applications()
    for app in applications:
        if uuid and app.get('uuid') == uuid:
            return app
        if name and app.get('name') == name:
            # Optionally filter by project and environment
            if project_uuid and app.get('project_uuid') != project_uuid:
                continue
            if environment_name and app.get('environment', {}).get('name') != environment_name:
                continue
            return app
    return None


def run_module():
    module_args = dict(
        api_url=dict(type='str', required=True),
        api_token=dict(type='str', required=True, no_log=True),
        state=dict(type='str', choices=['present', 'absent', 'started', 'stopped', 'restarted', 'deployed'], default='present'),
        uuid=dict(type='str'),
        name=dict(type='str'),
        application_type=dict(type='str', choices=['public', 'private-github-app', 'private-deploy-key', 'dockerfile', 'dockerimage', 'dockercompose']),
        project_uuid=dict(type='str'),
        server_uuid=dict(type='str'),
        environment_name=dict(type='str'),
        environment_uuid=dict(type='str'),
        description=dict(type='str'),
        git_repository=dict(type='str'),
        git_branch=dict(type='str'),
        build_pack=dict(type='str', choices=['nixpacks', 'static', 'dockerfile', 'dockercompose']),
        ports_exposes=dict(type='str'),
        domains=dict(type='str'),
        dockerfile=dict(type='str'),
        docker_registry_image_name=dict(type='str'),
        docker_registry_image_tag=dict(type='str'),
        docker_compose_raw=dict(type='str'),
        instant_deploy=dict(type='bool', default=False),
        delete_configurations=dict(type='bool', default=True),
        delete_volumes=dict(type='bool', default=True),
        timeout=dict(type='int', default=30),
        verify_ssl=dict(type='bool', default=True),
    )

    result = dict(
        changed=False,
        application=None,
        uuid=None,
        deployment_uuid=None,
        msg='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[
            ('state', 'present', ['name']),
            ('state', 'started', ['uuid', 'name'], True),
            ('state', 'stopped', ['uuid', 'name'], True),
            ('state', 'restarted', ['uuid', 'name'], True),
            ('state', 'deployed', ['uuid', 'name'], True),
        ],
        required_one_of=[
            ['uuid', 'name'],
        ],
    )

    state = module.params['state']
    uuid = module.params['uuid']
    name = module.params['name']
    app_type = module.params['application_type']

    try:
        client = CoolifyClient(
            base_url=module.params['api_url'],
            api_token=module.params['api_token'],
            timeout=module.params['timeout'],
            verify_ssl=module.params['verify_ssl'],
        )

        # Find existing application
        existing = find_application(
            client,
            name=name,
            uuid=uuid,
            project_uuid=module.params['project_uuid'],
            environment_name=module.params['environment_name'],
        )

        if state == 'present':
            if existing:
                result['application'] = existing
                result['uuid'] = existing['uuid']
                result['msg'] = f"Application '{name or uuid}' already exists"
                # TODO: Add update logic for mutable fields
            else:
                # Create new application
                if not app_type:
                    module.fail_json(msg="application_type is required when creating a new application")
                if not module.params['project_uuid']:
                    module.fail_json(msg="project_uuid is required when creating a new application")
                if not module.params['server_uuid']:
                    module.fail_json(msg="server_uuid is required when creating a new application")

                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = f"Would create application '{name}'"
                else:
                    # Build creation parameters based on type
                    create_params = {
                        'name': name,
                        'description': module.params['description'],
                        'project_uuid': module.params['project_uuid'],
                        'server_uuid': module.params['server_uuid'],
                        'environment_name': module.params['environment_name'],
                        'environment_uuid': module.params['environment_uuid'],
                        'git_repository': module.params['git_repository'],
                        'git_branch': module.params['git_branch'],
                        'build_pack': module.params['build_pack'],
                        'ports_exposes': module.params['ports_exposes'],
                        'domains': module.params['domains'],
                        'dockerfile': module.params['dockerfile'],
                        'docker_registry_image_name': module.params['docker_registry_image_name'],
                        'docker_registry_image_tag': module.params['docker_registry_image_tag'],
                        'docker_compose_raw': module.params['docker_compose_raw'],
                        'instant_deploy': module.params['instant_deploy'],
                    }

                    app = client.create_application(app_type, **create_params)
                    result['application'] = app
                    result['uuid'] = app.get('uuid')
                    result['changed'] = True
                    result['msg'] = f"Application '{name}' created"

        elif state == 'absent':
            if existing:
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = f"Would delete application '{name or uuid}'"
                else:
                    client.delete_application(
                        existing['uuid'],
                        delete_configurations=module.params['delete_configurations'],
                        delete_volumes=module.params['delete_volumes'],
                    )
                    result['changed'] = True
                    result['msg'] = f"Application '{name or uuid}' deleted"
            else:
                result['msg'] = f"Application '{name or uuid}' does not exist"

        elif state == 'started':
            if not existing:
                module.fail_json(msg=f"Application '{name or uuid}' not found")
            if module.check_mode:
                result['changed'] = True
                result['msg'] = f"Would start application '{name or uuid}'"
            else:
                client.start_application(existing['uuid'])
                result['application'] = existing
                result['uuid'] = existing['uuid']
                result['changed'] = True
                result['msg'] = f"Application '{name or uuid}' started"

        elif state == 'stopped':
            if not existing:
                module.fail_json(msg=f"Application '{name or uuid}' not found")
            if module.check_mode:
                result['changed'] = True
                result['msg'] = f"Would stop application '{name or uuid}'"
            else:
                client.stop_application(existing['uuid'])
                result['application'] = existing
                result['uuid'] = existing['uuid']
                result['changed'] = True
                result['msg'] = f"Application '{name or uuid}' stopped"

        elif state == 'restarted':
            if not existing:
                module.fail_json(msg=f"Application '{name or uuid}' not found")
            if module.check_mode:
                result['changed'] = True
                result['msg'] = f"Would restart application '{name or uuid}'"
            else:
                client.restart_application(existing['uuid'])
                result['application'] = existing
                result['uuid'] = existing['uuid']
                result['changed'] = True
                result['msg'] = f"Application '{name or uuid}' restarted"

        elif state == 'deployed':
            if not existing:
                module.fail_json(msg=f"Application '{name or uuid}' not found")
            if module.check_mode:
                result['changed'] = True
                result['msg'] = f"Would deploy application '{name or uuid}'"
            else:
                deploy_result = client.deploy_application(existing['uuid'])
                result['application'] = existing
                result['uuid'] = existing['uuid']
                result['deployment_uuid'] = deploy_result.get('deployment_uuid')
                result['changed'] = True
                result['msg'] = f"Application '{name or uuid}' deployment triggered"

    except Exception as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
