#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Coolify Collection
# EUPL-1.2 License

"""
Ansible module for managing Coolify projects and environments.

This is a self-contained module that includes the HTTP client directly
to avoid module_utils import issues with role-based modules.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: coolify_project
short_description: Manage Coolify projects and environments
description:
    - Create, update, and delete projects in Coolify.
    - Optionally manage environments within projects.
    - Provides idempotent project management.
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
        description: Desired state of the project
        type: str
        choices: ['present', 'absent']
        default: present
    name:
        description: Project name
        type: str
        required: true
    description:
        description: Project description
        type: str
    uuid:
        description: Project UUID (for updates/deletes by UUID)
        type: str
    environments:
        description: |
            List of environments to manage within the project.
            Each environment should have 'name' and optionally 'description'.
        type: list
        elements: dict
        suboptions:
            name:
                description: Environment name
                type: str
                required: true
            description:
                description: Environment description
                type: str
            state:
                description: Desired state of the environment
                type: str
                choices: ['present', 'absent']
                default: present
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
- name: Create a project
  coolify_project:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: present
    name: "my-app"
    description: "My Application Project"

- name: Create project with environments
  coolify_project:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: present
    name: "web-platform"
    description: "Web Platform Project"
    environments:
      - name: production
        description: "Production environment"
      - name: staging
        description: "Staging environment"
      - name: development
        description: "Development environment"

- name: Remove an environment from project
  coolify_project:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: present
    name: "web-platform"
    environments:
      - name: old-staging
        state: absent

- name: Delete a project
  coolify_project:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: absent
    name: "old-project"
'''

RETURN = r'''
project:
    description: The project details
    type: dict
    returned: when state is present
    sample:
        uuid: "abc123"
        name: "my-app"
        description: "My Application Project"
uuid:
    description: The project UUID
    type: str
    returned: when project exists
environments:
    description: List of environments in the project
    type: list
    returned: when project exists
environments_changed:
    description: List of environment changes made
    type: list
    returned: when environments were modified
'''

import json
import ssl
import urllib.request
import urllib.error

from ansible.module_utils.basic import AnsibleModule


class CoolifyClient:
    """Minimal Coolify API client for project operations."""

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

    # Project operations
    def list_projects(self):
        """List all projects."""
        return self._request('GET', '/projects')

    def get_project(self, uuid):
        """Get project by UUID."""
        return self._request('GET', f'/projects/{uuid}')

    def create_project(self, name, description=None):
        """Create a new project."""
        data = {'name': name}
        if description:
            data['description'] = description
        return self._request('POST', '/projects', data)

    def update_project(self, uuid, name=None, description=None):
        """Update an existing project."""
        data = {}
        if name:
            data['name'] = name
        if description is not None:  # Allow empty string to clear description
            data['description'] = description
        if data:
            return self._request('PATCH', f'/projects/{uuid}', data)
        return None

    def delete_project(self, uuid):
        """Delete a project."""
        return self._request('DELETE', f'/projects/{uuid}')

    # Environment operations
    def list_environments(self, project_uuid):
        """List environments in a project."""
        return self._request('GET', f'/projects/{project_uuid}/environments')

    def get_environment(self, project_uuid, env_name_or_uuid):
        """Get environment by name or UUID."""
        return self._request('GET', f'/projects/{project_uuid}/{env_name_or_uuid}')

    def create_environment(self, project_uuid, name, description=None):
        """Create a new environment in a project."""
        data = {'name': name}
        if description:
            data['description'] = description
        return self._request('POST', f'/projects/{project_uuid}/environments', data)

    def delete_environment(self, project_uuid, env_name_or_uuid):
        """Delete an environment from a project."""
        return self._request('DELETE', f'/projects/{project_uuid}/environments/{env_name_or_uuid}')


def find_project(client, name=None, uuid=None):
    """Find a project by name or UUID."""
    projects = client.list_projects()
    for project in projects:
        if uuid and project.get('uuid') == uuid:
            return project
        if name and project.get('name') == name:
            return project
    return None


def find_environment(environments, name):
    """Find an environment by name in a list."""
    for env in environments:
        if env.get('name') == name:
            return env
    return None


def needs_update(existing, params):
    """Check if existing project needs update."""
    if params.get('description') is not None:
        if existing.get('description') != params['description']:
            return True
    return False


def run_module():
    environment_spec = dict(
        name=dict(type='str', required=True),
        description=dict(type='str'),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )

    module_args = dict(
        api_url=dict(type='str', required=True),
        api_token=dict(type='str', required=True, no_log=True),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        name=dict(type='str', required=True),
        description=dict(type='str'),
        uuid=dict(type='str'),
        environments=dict(type='list', elements='dict', options=environment_spec),
        timeout=dict(type='int', default=30),
        verify_ssl=dict(type='bool', default=True),
    )

    result = dict(
        changed=False,
        project=None,
        uuid=None,
        environments=[],
        environments_changed=[],
        msg='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    state = module.params['state']
    name = module.params['name']
    description = module.params['description']
    uuid = module.params['uuid']
    environments = module.params['environments'] or []

    try:
        client = CoolifyClient(
            base_url=module.params['api_url'],
            api_token=module.params['api_token'],
            timeout=module.params['timeout'],
            verify_ssl=module.params['verify_ssl'],
        )

        # Find existing project
        existing = find_project(client, name=name, uuid=uuid)

        if state == 'present':
            if existing:
                # Project exists
                result['project'] = existing
                result['uuid'] = existing['uuid']

                # Check if project needs update
                if needs_update(existing, module.params):
                    if module.check_mode:
                        result['changed'] = True
                        result['msg'] = f"Would update project '{name}'"
                    else:
                        updated = client.update_project(
                            uuid=existing['uuid'],
                            description=description,
                        )
                        if updated:
                            result['project'] = updated
                        result['changed'] = True
                        result['msg'] = f"Project '{name}' updated"
                else:
                    result['msg'] = f"Project '{name}' already exists"

            else:
                # Create new project
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = f"Would create project '{name}'"
                else:
                    project = client.create_project(
                        name=name,
                        description=description,
                    )
                    result['project'] = project
                    result['uuid'] = project.get('uuid')
                    result['changed'] = True
                    result['msg'] = f"Project '{name}' created"
                    existing = project  # Use for environment management

            # Manage environments if project exists or was created
            if existing and environments and not module.check_mode:
                project_uuid = existing.get('uuid') or result['uuid']
                if project_uuid:
                    current_envs = client.list_environments(project_uuid)
                    result['environments'] = current_envs

                    for env_spec in environments:
                        env_name = env_spec['name']
                        env_state = env_spec.get('state', 'present')
                        env_description = env_spec.get('description')

                        existing_env = find_environment(current_envs, env_name)

                        if env_state == 'present':
                            if not existing_env:
                                # Create environment
                                client.create_environment(
                                    project_uuid=project_uuid,
                                    name=env_name,
                                    description=env_description,
                                )
                                result['environments_changed'].append({
                                    'name': env_name,
                                    'action': 'created'
                                })
                                result['changed'] = True
                        elif env_state == 'absent':
                            if existing_env:
                                # Delete environment
                                client.delete_environment(
                                    project_uuid=project_uuid,
                                    env_name_or_uuid=env_name,
                                )
                                result['environments_changed'].append({
                                    'name': env_name,
                                    'action': 'deleted'
                                })
                                result['changed'] = True

                    # Refresh environments list
                    result['environments'] = client.list_environments(project_uuid)

        elif state == 'absent':
            if existing:
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = f"Would delete project '{name}'"
                else:
                    client.delete_project(existing['uuid'])
                    result['changed'] = True
                    result['msg'] = f"Project '{name}' deleted"
            else:
                result['msg'] = f"Project '{name}' does not exist"

    except Exception as e:
        result['msg'] = str(e)
        module.fail_json(**result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
