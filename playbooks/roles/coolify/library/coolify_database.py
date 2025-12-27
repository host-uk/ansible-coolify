#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Coolify Collection
# EUPL-1.2 License

"""
Ansible module for managing Coolify databases.

This is a self-contained module that includes the HTTP client directly
to avoid module_utils import issues with role-based modules.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: coolify_database
short_description: Manage Coolify databases
description:
    - Create, update, delete, and control databases in Coolify.
    - Supports PostgreSQL, MySQL, MariaDB, MongoDB, Redis, KeyDB, DragonFly, and ClickHouse.
    - Provides idempotent database management.
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
        description: Desired state of the database
        type: str
        choices: ['present', 'absent', 'started', 'stopped', 'restarted']
        default: present
    uuid:
        description: Database UUID (for updates/deletes)
        type: str
    name:
        description: Database name
        type: str
    database_type:
        description: |
            Type of database to create.
            Required when creating a new database.
        type: str
        choices: ['postgresql', 'mysql', 'mariadb', 'mongodb', 'redis', 'keydb', 'dragonfly', 'clickhouse']
    project_uuid:
        description: UUID of the project where the database will be created
        type: str
    server_uuid:
        description: UUID of the server where the database will run
        type: str
    environment_name:
        description: Name of the environment (alternative to environment_uuid)
        type: str
    environment_uuid:
        description: UUID of the environment (alternative to environment_name)
        type: str
    description:
        description: Database description
        type: str
    image:
        description: Docker image to use (overrides default)
        type: str
    is_public:
        description: Make database publicly accessible
        type: bool
        default: false
    public_port:
        description: Port for public access
        type: int
    postgres_user:
        description: PostgreSQL username
        type: str
    postgres_password:
        description: PostgreSQL password
        type: str
    postgres_db:
        description: PostgreSQL database name
        type: str
    mysql_root_password:
        description: MySQL/MariaDB root password
        type: str
    mysql_user:
        description: MySQL/MariaDB username
        type: str
    mysql_password:
        description: MySQL/MariaDB password
        type: str
    mysql_database:
        description: MySQL/MariaDB database name
        type: str
    redis_password:
        description: Redis password
        type: str
    mongo_initdb_root_username:
        description: MongoDB root username
        type: str
    mongo_initdb_root_password:
        description: MongoDB root password
        type: str
    limits_memory:
        description: Memory limit (e.g., "512m", "1g")
        type: str
    limits_cpus:
        description: CPU limit (e.g., "0.5", "2")
        type: str
    delete_configurations:
        description: Delete configurations when removing database
        type: bool
        default: true
    delete_volumes:
        description: Delete volumes when removing database
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
- name: Create a PostgreSQL database
  coolify_database:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: present
    name: "app-db"
    database_type: postgresql
    project_uuid: "{{ project_uuid }}"
    server_uuid: "{{ server_uuid }}"
    environment_name: "production"
    postgres_user: "appuser"
    postgres_password: "{{ db_password }}"
    postgres_db: "appdb"

- name: Create a Redis instance
  coolify_database:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: present
    name: "cache"
    database_type: redis
    project_uuid: "{{ project_uuid }}"
    server_uuid: "{{ server_uuid }}"
    environment_name: "production"
    redis_password: "{{ redis_password }}"

- name: Start a database
  coolify_database:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: started
    uuid: "{{ db_uuid }}"

- name: Delete a database
  coolify_database:
    api_url: "http://localhost:8000/api/v1"
    api_token: "{{ coolify_api_token }}"
    state: absent
    uuid: "{{ db_uuid }}"
'''

RETURN = r'''
database:
    description: The database details
    type: dict
    returned: when state is present
uuid:
    description: The database UUID
    type: str
    returned: when database exists
'''

import json
import ssl
import urllib.request
import urllib.error

from ansible.module_utils.basic import AnsibleModule


class CoolifyClient:
    """Minimal Coolify API client for database operations."""

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

    def list_databases(self):
        """List all databases."""
        return self._request('GET', '/databases')

    def get_database(self, uuid):
        """Get database by UUID."""
        return self._request('GET', f'/databases/{uuid}')

    def create_database(self, db_type, **kwargs):
        """Create a new database based on type."""
        type_endpoints = {
            'postgresql': '/databases/postgresql',
            'mysql': '/databases/mysql',
            'mariadb': '/databases/mariadb',
            'mongodb': '/databases/mongodb',
            'redis': '/databases/redis',
            'keydb': '/databases/keydb',
            'dragonfly': '/databases/dragonfly',
            'clickhouse': '/databases/clickhouse',
        }
        endpoint = type_endpoints.get(db_type)
        if not endpoint:
            raise Exception(f"Unknown database type: {db_type}")

        # Filter out None values
        data = {k: v for k, v in kwargs.items() if v is not None}
        return self._request('POST', endpoint, data)

    def update_database(self, uuid, **kwargs):
        """Update an existing database."""
        data = {k: v for k, v in kwargs.items() if v is not None}
        if data:
            return self._request('PATCH', f'/databases/{uuid}', data)
        return None

    def delete_database(self, uuid, delete_configurations=True, delete_volumes=True):
        """Delete a database."""
        params = []
        if delete_configurations:
            params.append('delete_configurations=true')
        if delete_volumes:
            params.append('delete_volumes=true')
        query = '?' + '&'.join(params) if params else ''
        return self._request('DELETE', f'/databases/{uuid}{query}')

    def start_database(self, uuid):
        """Start a database."""
        return self._request('POST', f'/databases/{uuid}/start')

    def stop_database(self, uuid):
        """Stop a database."""
        return self._request('POST', f'/databases/{uuid}/stop')

    def restart_database(self, uuid):
        """Restart a database."""
        return self._request('POST', f'/databases/{uuid}/restart')


def find_database(client, name=None, uuid=None):
    """Find a database by name or UUID."""
    databases = client.list_databases()
    for db in databases:
        if uuid and db.get('uuid') == uuid:
            return db
        if name and db.get('name') == name:
            return db
    return None


def run_module():
    module_args = dict(
        api_url=dict(type='str', required=True),
        api_token=dict(type='str', required=True, no_log=True),
        state=dict(type='str', choices=['present', 'absent', 'started', 'stopped', 'restarted'], default='present'),
        uuid=dict(type='str'),
        name=dict(type='str'),
        database_type=dict(type='str', choices=['postgresql', 'mysql', 'mariadb', 'mongodb', 'redis', 'keydb', 'dragonfly', 'clickhouse']),
        project_uuid=dict(type='str'),
        server_uuid=dict(type='str'),
        environment_name=dict(type='str'),
        environment_uuid=dict(type='str'),
        description=dict(type='str'),
        image=dict(type='str'),
        is_public=dict(type='bool', default=False),
        public_port=dict(type='int'),
        # PostgreSQL specific
        postgres_user=dict(type='str'),
        postgres_password=dict(type='str', no_log=True),
        postgres_db=dict(type='str'),
        # MySQL/MariaDB specific
        mysql_root_password=dict(type='str', no_log=True),
        mysql_user=dict(type='str'),
        mysql_password=dict(type='str', no_log=True),
        mysql_database=dict(type='str'),
        # Redis specific
        redis_password=dict(type='str', no_log=True),
        # MongoDB specific
        mongo_initdb_root_username=dict(type='str'),
        mongo_initdb_root_password=dict(type='str', no_log=True),
        # Resource limits
        limits_memory=dict(type='str'),
        limits_cpus=dict(type='str'),
        # Delete options
        delete_configurations=dict(type='bool', default=True),
        delete_volumes=dict(type='bool', default=True),
        timeout=dict(type='int', default=30),
        verify_ssl=dict(type='bool', default=True),
    )

    result = dict(
        changed=False,
        database=None,
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
    db_type = module.params['database_type']

    try:
        client = CoolifyClient(
            base_url=module.params['api_url'],
            api_token=module.params['api_token'],
            timeout=module.params['timeout'],
            verify_ssl=module.params['verify_ssl'],
        )

        # Find existing database
        existing = find_database(client, name=name, uuid=uuid)

        if state == 'present':
            if existing:
                result['database'] = existing
                result['uuid'] = existing['uuid']
                result['msg'] = f"Database '{name or uuid}' already exists"
            else:
                # Create new database
                if not db_type:
                    module.fail_json(msg="database_type is required when creating a new database")
                if not module.params['project_uuid']:
                    module.fail_json(msg="project_uuid is required when creating a new database")
                if not module.params['server_uuid']:
                    module.fail_json(msg="server_uuid is required when creating a new database")

                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = f"Would create database '{name}'"
                else:
                    # Build creation parameters
                    create_params = {
                        'name': name,
                        'description': module.params['description'],
                        'project_uuid': module.params['project_uuid'],
                        'server_uuid': module.params['server_uuid'],
                        'environment_name': module.params['environment_name'],
                        'environment_uuid': module.params['environment_uuid'],
                        'image': module.params['image'],
                        'is_public': module.params['is_public'],
                        'public_port': module.params['public_port'],
                        'limits_memory': module.params['limits_memory'],
                        'limits_cpus': module.params['limits_cpus'],
                    }

                    # Add type-specific parameters
                    if db_type == 'postgresql':
                        create_params.update({
                            'postgres_user': module.params['postgres_user'],
                            'postgres_password': module.params['postgres_password'],
                            'postgres_db': module.params['postgres_db'],
                        })
                    elif db_type in ['mysql', 'mariadb']:
                        create_params.update({
                            'mysql_root_password': module.params['mysql_root_password'],
                            'mysql_user': module.params['mysql_user'],
                            'mysql_password': module.params['mysql_password'],
                            'mysql_database': module.params['mysql_database'],
                        })
                    elif db_type == 'redis':
                        create_params.update({
                            'redis_password': module.params['redis_password'],
                        })
                    elif db_type == 'mongodb':
                        create_params.update({
                            'mongo_initdb_root_username': module.params['mongo_initdb_root_username'],
                            'mongo_initdb_root_password': module.params['mongo_initdb_root_password'],
                        })

                    db = client.create_database(db_type, **create_params)
                    result['database'] = db
                    result['uuid'] = db.get('uuid')
                    result['changed'] = True
                    result['msg'] = f"Database '{name}' created"

        elif state == 'absent':
            if existing:
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = f"Would delete database '{name or uuid}'"
                else:
                    client.delete_database(
                        existing['uuid'],
                        delete_configurations=module.params['delete_configurations'],
                        delete_volumes=module.params['delete_volumes'],
                    )
                    result['changed'] = True
                    result['msg'] = f"Database '{name or uuid}' deleted"
            else:
                result['msg'] = f"Database '{name or uuid}' does not exist"

        elif state == 'started':
            if not existing:
                module.fail_json(msg=f"Database '{name or uuid}' not found")
            if module.check_mode:
                result['changed'] = True
                result['msg'] = f"Would start database '{name or uuid}'"
            else:
                client.start_database(existing['uuid'])
                result['database'] = existing
                result['uuid'] = existing['uuid']
                result['changed'] = True
                result['msg'] = f"Database '{name or uuid}' started"

        elif state == 'stopped':
            if not existing:
                module.fail_json(msg=f"Database '{name or uuid}' not found")
            if module.check_mode:
                result['changed'] = True
                result['msg'] = f"Would stop database '{name or uuid}'"
            else:
                client.stop_database(existing['uuid'])
                result['database'] = existing
                result['uuid'] = existing['uuid']
                result['changed'] = True
                result['msg'] = f"Database '{name or uuid}' stopped"

        elif state == 'restarted':
            if not existing:
                module.fail_json(msg=f"Database '{name or uuid}' not found")
            if module.check_mode:
                result['changed'] = True
                result['msg'] = f"Would restart database '{name or uuid}'"
            else:
                client.restart_database(existing['uuid'])
                result['database'] = existing
                result['uuid'] = existing['uuid']
                result['changed'] = True
                result['msg'] = f"Database '{name or uuid}' restarted"

    except Exception as e:
        result['msg'] = str(e)
        module.fail_json(**result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
