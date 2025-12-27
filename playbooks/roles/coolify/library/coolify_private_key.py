#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Coolify Collection
# EUPL-1.2 License

"""
Ansible module for managing Coolify private keys.

This is a self-contained module that includes the HTTP client directly
to avoid module_utils import issues with role-based modules.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: coolify_private_key
short_description: Manage Coolify private keys
description:
    - Create, update, and delete private keys in Coolify.
    - Private keys are used for SSH authentication to servers.
    - Provides idempotent key management.
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
        description: Desired state of the private key
        type: str
        choices: ['present', 'absent']
        default: present
    name:
        description: Private key name (used for identification)
        type: str
        required: true
    description:
        description: Private key description
        type: str
    private_key:
        description: |
            The private key content in PEM format.
            Required when state=present and creating a new key.
        type: str
    private_key_file:
        description: |
            Path to a file containing the private key.
            Alternative to private_key parameter.
        type: path
    uuid:
        description: Private key UUID (for updates/deletes by UUID)
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
- name: Create a private key
  coolify_private_key:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: present
    name: "worker-ssh-key"
    description: "SSH key for worker nodes"
    private_key: "{{ lookup('file', '~/.ssh/worker_key') }}"

- name: Create key from file
  coolify_private_key:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: present
    name: "deploy-key"
    private_key_file: "/path/to/deploy_key"

- name: Remove a private key
  coolify_private_key:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: absent
    name: "old-key"

- name: Remove key by UUID
  coolify_private_key:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: absent
    uuid: "abc123-def456"
'''

RETURN = r'''
private_key:
    description: The private key details (without the actual key content)
    type: dict
    returned: when state is present
    sample:
        uuid: "abc123"
        name: "worker-ssh-key"
        description: "SSH key for worker nodes"
uuid:
    description: The private key UUID
    type: str
    returned: when key exists
'''

import json
import ssl
import urllib.request
import urllib.error
import os

from ansible.module_utils.basic import AnsibleModule


class CoolifyClient:
    """Minimal Coolify API client for private key operations."""

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

    def list_private_keys(self):
        """List all private keys."""
        return self._request('GET', '/security/keys')

    def get_private_key(self, uuid):
        """Get private key by UUID."""
        return self._request('GET', f'/security/keys/{uuid}')

    def create_private_key(self, name, private_key, description=None):
        """Create a new private key."""
        data = {
            'name': name,
            'private_key': private_key,
        }
        if description:
            data['description'] = description
        return self._request('POST', '/security/keys', data)

    def update_private_key(self, uuid, name=None, description=None):
        """Update an existing private key (name and description only)."""
        data = {}
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        if data:
            return self._request('PATCH', f'/security/keys/{uuid}', data)
        return None

    def delete_private_key(self, uuid):
        """Delete a private key."""
        return self._request('DELETE', f'/security/keys/{uuid}')


def find_private_key(client, name=None, uuid=None):
    """Find a private key by name or UUID."""
    keys = client.list_private_keys()
    for key in keys:
        if uuid and key.get('uuid') == uuid:
            return key
        if name and key.get('name') == name:
            return key
    return None


def needs_update(existing, params):
    """Check if existing key needs update (description only, name is identifier)."""
    if params.get('description') is not None:
        if existing.get('description') != params['description']:
            return True
    return False


def run_module():
    module_args = dict(
        api_url=dict(type='str', required=True),
        api_token=dict(type='str', required=True, no_log=True),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        name=dict(type='str', required=True),
        description=dict(type='str'),
        private_key=dict(type='str', no_log=True),
        private_key_file=dict(type='path'),
        uuid=dict(type='str'),
        timeout=dict(type='int', default=30),
        verify_ssl=dict(type='bool', default=True),
    )

    result = dict(
        changed=False,
        private_key=None,
        uuid=None,
        msg='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[
            ('private_key', 'private_key_file'),
        ],
    )

    state = module.params['state']
    name = module.params['name']
    description = module.params['description']
    private_key = module.params['private_key']
    private_key_file = module.params['private_key_file']
    uuid = module.params['uuid']

    # Read private key from file if specified
    if private_key_file:
        try:
            with open(os.path.expanduser(private_key_file), 'r') as f:
                private_key = f.read()
        except IOError as e:
            module.fail_json(msg=f"Failed to read private key file: {e}")

    try:
        client = CoolifyClient(
            base_url=module.params['api_url'],
            api_token=module.params['api_token'],
            timeout=module.params['timeout'],
            verify_ssl=module.params['verify_ssl'],
        )

        # Find existing key
        existing = find_private_key(client, name=name, uuid=uuid)

        if state == 'present':
            if existing:
                # Key exists - check if update needed
                result['private_key'] = existing
                result['uuid'] = existing['uuid']

                if needs_update(existing, module.params):
                    if module.check_mode:
                        result['changed'] = True
                        result['msg'] = f"Would update private key '{name}'"
                    else:
                        updated = client.update_private_key(
                            uuid=existing['uuid'],
                            description=description,
                        )
                        if updated:
                            result['private_key'] = updated
                        result['changed'] = True
                        result['msg'] = f"Private key '{name}' updated"
                else:
                    result['msg'] = f"Private key '{name}' already exists (no changes)"
            else:
                # Create new key
                if not private_key:
                    module.fail_json(msg="private_key or private_key_file is required when creating a new key")

                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = f"Would create private key '{name}'"
                else:
                    key = client.create_private_key(
                        name=name,
                        private_key=private_key,
                        description=description,
                    )
                    result['private_key'] = key
                    result['uuid'] = key.get('uuid')
                    result['changed'] = True
                    result['msg'] = f"Private key '{name}' created"

        elif state == 'absent':
            if existing:
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = f"Would delete private key '{name}'"
                else:
                    client.delete_private_key(existing['uuid'])
                    result['changed'] = True
                    result['msg'] = f"Private key '{name}' deleted"
            else:
                result['msg'] = f"Private key '{name}' does not exist"

    except Exception as e:
        result['msg'] = str(e)
        module.fail_json(**result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
