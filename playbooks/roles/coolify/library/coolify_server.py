#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Coolify Collection
# EUPL-1.2 License

"""
Ansible module for managing Coolify servers.

This is a self-contained module that includes the HTTP client directly
to avoid module_utils import issues with role-based modules.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: coolify_server
short_description: Manage Coolify servers
description:
    - Create, update, delete, and validate servers in Coolify.
    - Provides idempotent server management.
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
        description: Desired state of the server
        type: str
        choices: ['present', 'absent', 'validated']
        default: present
    name:
        description: Server name
        type: str
        required: true
    ip:
        description: Server IP address
        type: str
    private_key_uuid:
        description: UUID of the private key for SSH access
        type: str
    port:
        description: SSH port
        type: int
        default: 22
    user:
        description: SSH user
        type: str
        default: root
    description:
        description: Server description
        type: str
    is_build_server:
        description: Whether this is a build server
        type: bool
        default: false
    uuid:
        description: Server UUID (for updates/deletes)
        type: str
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
- name: Create a server
  coolify_server:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: present
    name: "worker-1"
    ip: "192.168.1.100"
    private_key_uuid: "{{ key_uuid }}"
    is_build_server: false

- name: Validate a server (install Docker, etc.)
  coolify_server:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: validated
    name: "worker-1"

- name: Remove a server
  coolify_server:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: absent
    name: "worker-1"
'''

RETURN = r'''
server:
    description: The server details
    type: dict
    returned: when state is present or validated
uuid:
    description: The server UUID
    type: str
    returned: when server exists
validation_result:
    description: Result of server validation
    type: dict
    returned: when state is validated
'''

import json
import ssl
import urllib.request
import urllib.error
import urllib.parse

from ansible.module_utils.basic import AnsibleModule


class CoolifyClient:
    """Minimal Coolify API client."""

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

    def list_servers(self):
        """List all servers."""
        return self._request('GET', '/servers')

    def get_server(self, uuid):
        """Get server by UUID."""
        return self._request('GET', f'/servers/{uuid}')

    def create_server(self, name, ip, private_key_uuid, port=22, user='root',
                      description=None, is_build_server=False):
        """Create a new server."""
        data = {
            'name': name,
            'ip': ip,
            'private_key_uuid': private_key_uuid,
            'port': port,
            'user': user,
        }
        if description:
            data['description'] = description
        if is_build_server:
            data['is_build_server'] = is_build_server
        return self._request('POST', '/servers', data)

    def delete_server(self, uuid):
        """Delete a server."""
        return self._request('DELETE', f'/servers/{uuid}')

    def validate_server(self, uuid):
        """Validate/initialize a server."""
        return self._request('GET', f'/servers/{uuid}/validate')


def find_server(client, name=None, ip=None, uuid=None):
    """Find a server by name, IP, or UUID."""
    servers = client.list_servers()
    for server in servers:
        if uuid and server.get('uuid') == uuid:
            return server
        if name and server.get('name') == name:
            return server
        if ip and server.get('ip') == ip:
            return server
    return None


def run_module():
    module_args = dict(
        api_url=dict(type='str', required=True),
        api_token=dict(type='str', required=True, no_log=True),
        state=dict(type='str', choices=['present', 'absent', 'validated'], default='present'),
        name=dict(type='str', required=True),
        ip=dict(type='str'),
        private_key_uuid=dict(type='str'),
        port=dict(type='int', default=22),
        user=dict(type='str', default='root'),
        description=dict(type='str'),
        is_build_server=dict(type='bool', default=False),
        uuid=dict(type='str'),
        timeout=dict(type='int', default=30),
        verify_ssl=dict(type='bool', default=True),
    )

    result = dict(
        changed=False,
        server=None,
        uuid=None,
        validation_result=None,
        msg='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[
            ('state', 'present', ['ip', 'private_key_uuid']),
        ],
    )

    state = module.params['state']
    name = module.params['name']
    ip = module.params['ip']
    private_key_uuid = module.params['private_key_uuid']
    port = module.params['port']
    user = module.params['user']
    description = module.params['description']
    is_build_server = module.params['is_build_server']
    uuid = module.params['uuid']

    try:
        client = CoolifyClient(
            base_url=module.params['api_url'],
            api_token=module.params['api_token'],
            timeout=module.params['timeout'],
            verify_ssl=module.params['verify_ssl'],
        )

        # Find existing server
        existing = find_server(client, name=name, ip=ip, uuid=uuid)

        if state == 'present':
            if existing:
                result['server'] = existing
                result['uuid'] = existing['uuid']
                result['msg'] = f"Server '{name}' already exists"
            else:
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = f"Would create server '{name}'"
                else:
                    server = client.create_server(
                        name=name,
                        ip=ip,
                        private_key_uuid=private_key_uuid,
                        port=port,
                        user=user,
                        description=description,
                        is_build_server=is_build_server,
                    )
                    result['server'] = server
                    result['uuid'] = server.get('uuid')
                    result['changed'] = True
                    result['msg'] = f"Server '{name}' created"

        elif state == 'absent':
            if existing:
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = f"Would delete server '{name}'"
                else:
                    client.delete_server(existing['uuid'])
                    result['changed'] = True
                    result['msg'] = f"Server '{name}' deleted"
            else:
                result['msg'] = f"Server '{name}' does not exist"

        elif state == 'validated':
            if not existing:
                module.fail_json(msg=f"Server '{name}' not found. Create it first with state=present")

            result['server'] = existing
            result['uuid'] = existing['uuid']

            if module.check_mode:
                result['changed'] = True
                result['msg'] = f"Would validate server '{name}'"
            else:
                validation = client.validate_server(existing['uuid'])
                result['validation_result'] = validation
                result['changed'] = True
                result['msg'] = f"Validation started for server '{name}'"

    except Exception as e:
        result['msg'] = str(e)
        module.fail_json(**result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
