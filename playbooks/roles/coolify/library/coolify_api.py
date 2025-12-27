#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Coolify Collection
# EUPL-1.2 License

"""
Ansible module for interacting with the Coolify API.

This module provides a generic interface to call any Coolify API operation
using the OpenAPI specification.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: coolify_api
short_description: Interact with the Coolify API
description:
    - This module allows you to call any Coolify API operation.
    - Uses the Coolify OpenAPI specification for automatic endpoint discovery.
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
    operation:
        description: The API operation to call (operationId from OpenAPI spec)
        type: str
        required: true
    params:
        description: Parameters for the API operation
        type: dict
        default: {}
    timeout:
        description: Request timeout in seconds
        type: int
        default: 30
    verify_ssl:
        description: Whether to verify SSL certificates
        type: bool
        default: true
notes:
    - The module uses the Coolify OpenAPI specification bundled with the role.
    - Common operations include: list-servers, validate-server-by-uuid, create-project, etc.
'''

EXAMPLES = r'''
- name: List all servers
  coolify_api:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    operation: list-servers

- name: Validate a server
  coolify_api:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    operation: validate-server-by-uuid
    params:
      uuid: "abc123-def456"

- name: Create a project
  coolify_api:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    operation: create-project
    params:
      name: "my-project"
      description: "My awesome project"

- name: Get server resources
  coolify_api:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    operation: get-resources-by-server-uuid
    params:
      uuid: "{{ server_uuid }}"
'''

RETURN = r'''
response:
    description: The API response
    type: dict
    returned: always
operation:
    description: The operation that was called
    type: str
    returned: always
'''

import os
import sys
import json

from ansible.module_utils.basic import AnsibleModule

# Add module_utils path for imports - try multiple paths
possible_paths = [
    os.path.join(os.path.dirname(__file__), '..', 'module_utils'),
    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'roles', 'coolify', 'module_utils'),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'module_utils'),
]
for path in possible_paths:
    abs_path = os.path.abspath(path)
    if os.path.exists(abs_path) and abs_path not in sys.path:
        sys.path.insert(0, abs_path)

try:
    from swagger.coolify_api import CoolifyClient, CoolifyError
    HAS_CLIENT = True
    IMPORT_ERROR = None
except ImportError as e:
    HAS_CLIENT = False
    IMPORT_ERROR = str(e)


def run_module():
    module_args = dict(
        api_url=dict(type='str', required=True),
        api_token=dict(type='str', required=True, no_log=True),
        operation=dict(type='str', required=True),
        params=dict(type='dict', default={}),
        timeout=dict(type='int', default=30),
        verify_ssl=dict(type='bool', default=True),
    )

    result = dict(
        changed=False,
        response=None,
        operation=None,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if not HAS_CLIENT:
        module.fail_json(msg=f'Failed to import coolify_api client: {IMPORT_ERROR}')

    api_url = module.params['api_url']
    api_token = module.params['api_token']
    operation = module.params['operation']
    params = module.params['params']
    timeout = module.params['timeout']
    verify_ssl = module.params['verify_ssl']

    result['operation'] = operation

    # Check mode - don't make actual API calls
    if module.check_mode:
        result['response'] = {'check_mode': True, 'operation': operation}
        module.exit_json(**result)

    try:
        client = CoolifyClient(
            base_url=api_url,
            api_token=api_token,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )

        # Call the operation
        response = client._call(operation, params, check_response=False)
        result['response'] = response

        # Determine if this was a mutating operation
        mutating_ops = [
            'create-', 'update-', 'delete-', 'start-', 'stop-', 'restart-',
            'validate-', 'deploy-', 'cancel-'
        ]
        for prefix in mutating_ops:
            if operation.startswith(prefix):
                result['changed'] = True
                break

    except CoolifyError as e:
        module.fail_json(msg=str(e), **result)
    except Exception as e:
        module.fail_json(msg=f'Unexpected error: {str(e)}', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
