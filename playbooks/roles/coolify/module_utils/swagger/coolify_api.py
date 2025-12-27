# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Coolify Collection
# EUPL-1.2 License

"""
Coolify API Client using Swagger/OpenAPI specification.

This module provides a high-level interface to the Coolify API using the
generic SwaggerClient. It handles authentication, response parsing, and
provides convenience methods for common Coolify operations.

Usage:
    from coolify_api import CoolifyClient, CoolifyError

    # Create client
    client = CoolifyClient(
        base_url='http://localhost:8000/api/v1',
        api_token='your-api-token',
    )

    # List servers
    servers = client.list_servers()

    # Validate a server
    result = client.validate_server('server-uuid')
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
from .swagger_client import SwaggerClient, SwaggerClientError, load_swagger_spec


class CoolifyError(Exception):
    """Exception raised by Coolify operations."""

    def __init__(self, message, api_response=None):
        super(CoolifyError, self).__init__(message)
        self.api_response = api_response


def get_swagger_spec_path():
    """Get the path to the Coolify swagger spec file."""
    return os.path.join(os.path.dirname(__file__), 'coolify_openapi.json')


class CoolifyClient:
    """
    Coolify API client using Swagger specification.

    This client provides a Pythonic interface to the Coolify API, handling
    authentication and providing convenience methods for operations.
    """

    def __init__(
        self,
        base_url,
        api_token,
        timeout=30,
        verify_ssl=True,
        max_retries=3,
        spec_path=None,
    ):
        """
        Initialize the Coolify client.

        Args:
            base_url: Coolify API base URL (e.g., http://localhost:8000/api/v1)
            api_token: Bearer token for API authentication
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            max_retries: Maximum retry attempts for failed requests
            spec_path: Optional path to swagger spec file
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token

        # Load swagger spec
        spec_path = spec_path or get_swagger_spec_path()
        spec = load_swagger_spec(spec_path)

        # Create swagger client with Bearer auth
        self._client = SwaggerClient(
            spec=spec,
            base_url=self.base_url,
            auth_headers={'Authorization': f'Bearer {api_token}'},
            timeout=timeout,
            verify_ssl=verify_ssl,
            max_retries=max_retries,
        )

    def _check_response(self, response, operation_name):
        """Check API response for errors."""
        if isinstance(response, dict):
            if 'message' in response and 'error' in response.get('message', '').lower():
                raise CoolifyError(f"{operation_name} failed: {response['message']}", response)
        return response

    def _call(self, operation_id, params=None, check_response=True):
        """Call an API operation and optionally check for errors."""
        try:
            response = self._client.call_operation(operation_id, params)
            if check_response:
                return self._check_response(response, operation_id)
            return response
        except SwaggerClientError as e:
            raise CoolifyError(str(e))

    # =========================================================================
    # Health & Version
    # =========================================================================

    def healthcheck(self):
        """Check API health."""
        return self._call('healthcheck', check_response=False)

    def version(self):
        """Get Coolify version."""
        return self._call('version', check_response=False)

    # =========================================================================
    # Servers
    # =========================================================================

    def list_servers(self):
        """
        List all servers.

        Returns:
            list: List of server objects
        """
        return self._call('list-servers', check_response=False)

    def get_server(self, uuid):
        """
        Get server by UUID.

        Args:
            uuid: Server UUID

        Returns:
            dict: Server details
        """
        return self._call('get-server-by-uuid', {'uuid': uuid})

    def create_server(self, name, ip, private_key_uuid, port=22, user='root',
                      description=None, is_build_server=False):
        """
        Create a new server.

        Args:
            name: Server name
            ip: Server IP address
            private_key_uuid: UUID of the private key for SSH access
            port: SSH port (default: 22)
            user: SSH user (default: root)
            description: Server description
            is_build_server: Whether this is a build server

        Returns:
            dict: Created server details
        """
        params = {
            'name': name,
            'ip': ip,
            'private_key_uuid': private_key_uuid,
            'port': port,
            'user': user,
        }
        if description:
            params['description'] = description
        if is_build_server:
            params['is_build_server'] = is_build_server

        return self._call('create-server', params)

    def update_server(self, uuid, **kwargs):
        """
        Update server settings.

        Args:
            uuid: Server UUID
            **kwargs: Server properties to update

        Returns:
            dict: Updated server details
        """
        params = {'uuid': uuid}
        params.update(kwargs)
        return self._call('update-server-by-uuid', params)

    def delete_server(self, uuid):
        """
        Delete a server.

        Args:
            uuid: Server UUID

        Returns:
            dict: API response
        """
        return self._call('delete-server-by-uuid', {'uuid': uuid})

    def validate_server(self, uuid):
        """
        Validate/initialize a server. This installs Docker and required
        components on the server.

        Args:
            uuid: Server UUID

        Returns:
            dict: Validation result
        """
        return self._call('validate-server-by-uuid', {'uuid': uuid})

    def get_server_resources(self, uuid):
        """
        Get resources deployed on a server.

        Args:
            uuid: Server UUID

        Returns:
            list: Resources on the server
        """
        return self._call('get-resources-by-server-uuid', {'uuid': uuid})

    def get_server_domains(self, uuid):
        """
        Get domains configured on a server.

        Args:
            uuid: Server UUID

        Returns:
            list: Domains on the server
        """
        return self._call('get-domains-by-server-uuid', {'uuid': uuid})

    # =========================================================================
    # Private Keys
    # =========================================================================

    def list_private_keys(self):
        """List all private keys."""
        return self._call('list-private-keys', check_response=False)

    def get_private_key(self, uuid):
        """Get private key by UUID."""
        return self._call('get-private-key-by-uuid', {'uuid': uuid})

    def create_private_key(self, name, private_key, description=None):
        """
        Create a new private key.

        Args:
            name: Key name
            private_key: Private key content (PEM format)
            description: Key description

        Returns:
            dict: Created key details with UUID
        """
        params = {
            'name': name,
            'private_key': private_key,
        }
        if description:
            params['description'] = description
        return self._call('create-private-key', params)

    def update_private_key(self, uuid, **kwargs):
        """Update private key."""
        params = {'uuid': uuid}
        params.update(kwargs)
        return self._call('update-private-key', params)

    def delete_private_key(self, uuid):
        """Delete private key."""
        return self._call('delete-private-key-by-uuid', {'uuid': uuid})

    # =========================================================================
    # Projects
    # =========================================================================

    def list_projects(self):
        """List all projects."""
        return self._call('list-projects', check_response=False)

    def get_project(self, uuid):
        """Get project by UUID."""
        return self._call('get-project-by-uuid', {'uuid': uuid})

    def create_project(self, name, description=None):
        """
        Create a new project.

        Args:
            name: Project name
            description: Project description

        Returns:
            dict: Created project with UUID
        """
        params = {'name': name}
        if description:
            params['description'] = description
        return self._call('create-project', params)

    def update_project(self, uuid, **kwargs):
        """Update project."""
        params = {'uuid': uuid}
        params.update(kwargs)
        return self._call('update-project-by-uuid', params)

    def delete_project(self, uuid):
        """Delete project."""
        return self._call('delete-project-by-uuid', {'uuid': uuid})

    # =========================================================================
    # Environments
    # =========================================================================

    def get_environments(self, project_uuid):
        """
        Get all environments for a project.

        Args:
            project_uuid: Project UUID

        Returns:
            list: Environments in the project
        """
        return self._call('get-environments', {'uuid': project_uuid})

    def get_environment(self, project_uuid, environment_name_or_uuid):
        """
        Get environment by name or UUID.

        Args:
            project_uuid: Project UUID
            environment_name_or_uuid: Environment name or UUID

        Returns:
            dict: Environment details
        """
        return self._call('get-environment-by-name-or-uuid', {
            'uuid': project_uuid,
            'environment_name': environment_name_or_uuid,
        })

    def create_environment(self, project_uuid, name, description=None):
        """
        Create a new environment in a project.

        Args:
            project_uuid: Project UUID
            name: Environment name
            description: Environment description

        Returns:
            dict: Created environment
        """
        params = {
            'uuid': project_uuid,
            'name': name,
        }
        if description:
            params['description'] = description
        return self._call('create-environment', params)

    def delete_environment(self, project_uuid, environment_name_or_uuid):
        """Delete environment."""
        return self._call('delete-environment', {
            'uuid': project_uuid,
            'environment_name': environment_name_or_uuid,
        })

    # =========================================================================
    # Teams
    # =========================================================================

    def get_current_team(self):
        """Get current team."""
        return self._call('get-current-team', check_response=False)

    def get_current_team_members(self):
        """Get current team members."""
        return self._call('get-current-team-members', check_response=False)

    def list_teams(self):
        """List all teams."""
        return self._call('list-teams', check_response=False)

    def get_team(self, team_id):
        """Get team by ID."""
        return self._call('get-team-by-id', {'id': team_id})

    def get_team_members(self, team_id):
        """Get team members."""
        return self._call('get-members-by-team-id', {'id': team_id})

    # =========================================================================
    # Applications
    # =========================================================================

    def list_applications(self):
        """List all applications."""
        return self._call('list-applications', check_response=False)

    def get_application(self, uuid):
        """Get application by UUID."""
        return self._call('get-application-by-uuid', {'uuid': uuid})

    def create_public_application(self, project_uuid, server_uuid, environment_name,
                                   git_repository, git_branch, build_pack, ports_exposes,
                                   **kwargs):
        """
        Create application from public git repository.

        Args:
            project_uuid: Project UUID
            server_uuid: Server UUID to deploy on
            environment_name: Environment name
            git_repository: Git repository URL
            git_branch: Git branch
            build_pack: Build pack (e.g., 'nixpacks', 'dockerfile')
            ports_exposes: Ports to expose
            **kwargs: Additional application settings

        Returns:
            dict: Created application
        """
        params = {
            'project_uuid': project_uuid,
            'server_uuid': server_uuid,
            'environment_name': environment_name,
            'git_repository': git_repository,
            'git_branch': git_branch,
            'build_pack': build_pack,
            'ports_exposes': ports_exposes,
        }
        params.update(kwargs)
        return self._call('create-public-application', params)

    def update_application(self, uuid, **kwargs):
        """Update application."""
        params = {'uuid': uuid}
        params.update(kwargs)
        return self._call('update-application-by-uuid', params)

    def delete_application(self, uuid):
        """Delete application."""
        return self._call('delete-application-by-uuid', {'uuid': uuid})

    def start_application(self, uuid):
        """Start application."""
        return self._call('start-application-by-uuid', {'uuid': uuid})

    def stop_application(self, uuid):
        """Stop application."""
        return self._call('stop-application-by-uuid', {'uuid': uuid})

    def restart_application(self, uuid):
        """Restart application."""
        return self._call('restart-application-by-uuid', {'uuid': uuid})

    def get_application_logs(self, uuid):
        """Get application logs."""
        return self._call('get-application-logs-by-uuid', {'uuid': uuid})

    # =========================================================================
    # Environment Variables
    # =========================================================================

    def list_application_envs(self, uuid):
        """List environment variables for an application."""
        return self._call('list-envs-by-application-uuid', {'uuid': uuid})

    def create_application_env(self, uuid, key, value, is_preview=False, is_build_time=False):
        """Create environment variable for application."""
        return self._call('create-env-by-application-uuid', {
            'uuid': uuid,
            'key': key,
            'value': value,
            'is_preview': is_preview,
            'is_build_time': is_build_time,
        })

    def update_application_envs(self, uuid, envs):
        """Bulk update environment variables."""
        return self._call('update-envs-by-application-uuid', {
            'uuid': uuid,
            'data': envs,
        })

    def delete_application_env(self, uuid, env_uuid):
        """Delete environment variable."""
        return self._call('delete-env-by-application-uuid', {
            'uuid': uuid,
            'env_uuid': env_uuid,
        })

    # =========================================================================
    # Services (Docker Compose)
    # =========================================================================

    def list_services(self):
        """List all services."""
        return self._call('list-services', check_response=False)

    def get_service(self, uuid):
        """Get service by UUID."""
        return self._call('get-service-by-uuid', {'uuid': uuid})

    def create_service(self, server_uuid, project_uuid, environment_name,
                       docker_compose_raw, **kwargs):
        """
        Create a new service from docker-compose.

        Args:
            server_uuid: Server UUID
            project_uuid: Project UUID
            environment_name: Environment name
            docker_compose_raw: Docker Compose YAML content
            **kwargs: Additional service settings

        Returns:
            dict: Created service
        """
        params = {
            'server_uuid': server_uuid,
            'project_uuid': project_uuid,
            'environment_name': environment_name,
            'docker_compose_raw': docker_compose_raw,
        }
        params.update(kwargs)
        return self._call('create-service', params)

    def update_service(self, uuid, **kwargs):
        """Update service."""
        params = {'uuid': uuid}
        params.update(kwargs)
        return self._call('update-service-by-uuid', params)

    def delete_service(self, uuid):
        """Delete service."""
        return self._call('delete-service-by-uuid', {'uuid': uuid})

    def start_service(self, uuid):
        """Start service."""
        return self._call('start-service-by-uuid', {'uuid': uuid})

    def stop_service(self, uuid):
        """Stop service."""
        return self._call('stop-service-by-uuid', {'uuid': uuid})

    def restart_service(self, uuid):
        """Restart service."""
        return self._call('restart-service-by-uuid', {'uuid': uuid})

    # =========================================================================
    # Databases
    # =========================================================================

    def list_databases(self):
        """List all databases."""
        return self._call('list-databases', check_response=False)

    def get_database(self, uuid):
        """Get database by UUID."""
        return self._call('get-database-by-uuid', {'uuid': uuid})

    def create_postgresql(self, server_uuid, project_uuid, environment_name, **kwargs):
        """Create PostgreSQL database."""
        params = {
            'server_uuid': server_uuid,
            'project_uuid': project_uuid,
            'environment_name': environment_name,
        }
        params.update(kwargs)
        return self._call('create-database-postgresql', params)

    def create_mysql(self, server_uuid, project_uuid, environment_name, **kwargs):
        """Create MySQL database."""
        params = {
            'server_uuid': server_uuid,
            'project_uuid': project_uuid,
            'environment_name': environment_name,
        }
        params.update(kwargs)
        return self._call('create-database-mysql', params)

    def create_redis(self, server_uuid, project_uuid, environment_name, **kwargs):
        """Create Redis database."""
        params = {
            'server_uuid': server_uuid,
            'project_uuid': project_uuid,
            'environment_name': environment_name,
        }
        params.update(kwargs)
        return self._call('create-database-redis', params)

    def delete_database(self, uuid):
        """Delete database."""
        return self._call('delete-database-by-uuid', {'uuid': uuid})

    def start_database(self, uuid):
        """Start database."""
        return self._call('start-database-by-uuid', {'uuid': uuid})

    def stop_database(self, uuid):
        """Stop database."""
        return self._call('stop-database-by-uuid', {'uuid': uuid})

    def restart_database(self, uuid):
        """Restart database."""
        return self._call('restart-database-by-uuid', {'uuid': uuid})

    # =========================================================================
    # Deployments
    # =========================================================================

    def list_deployments(self):
        """List all deployments."""
        return self._call('list-deployments', check_response=False)

    def list_application_deployments(self, uuid):
        """List deployments for an application."""
        return self._call('list-deployments-by-app-uuid', {'uuid': uuid})

    def get_deployment(self, uuid):
        """Get deployment by UUID."""
        return self._call('get-deployment-by-uuid', {'uuid': uuid})

    def deploy(self, uuid=None, tag=None, force=False):
        """
        Deploy by UUID or tag.

        Args:
            uuid: Application/Service UUID
            tag: Deploy tag
            force: Force rebuild

        Returns:
            dict: Deployment result
        """
        params = {'force': force}
        if uuid:
            params['uuid'] = uuid
        if tag:
            params['tag'] = tag
        return self._call('deploy-by-tag-or-uuid', params)

    def cancel_deployment(self, uuid):
        """Cancel deployment."""
        return self._call('cancel-deployment-by-uuid', {'uuid': uuid})

    # =========================================================================
    # Resources
    # =========================================================================

    def list_resources(self):
        """List all resources (applications, services, databases)."""
        return self._call('list-resources', check_response=False)

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def ensure_server(self, name, ip, private_key_uuid, state='present', **kwargs):
        """
        Ensure a server exists or is absent (idempotent).

        Args:
            name: Server name
            ip: Server IP
            private_key_uuid: Private key UUID
            state: 'present' or 'absent'
            **kwargs: Additional server settings

        Returns:
            dict: Result with 'changed', 'msg', and 'data' keys
        """
        result = {'changed': False, 'msg': '', 'data': None}

        try:
            servers = self.list_servers()
            existing = None
            for server in servers:
                if server.get('ip') == ip or server.get('name') == name:
                    existing = server
                    break

            if state == 'present':
                if existing:
                    result['msg'] = f"Server '{name}' already exists"
                    result['data'] = existing
                else:
                    result['data'] = self.create_server(
                        name=name,
                        ip=ip,
                        private_key_uuid=private_key_uuid,
                        **kwargs
                    )
                    result['changed'] = True
                    result['msg'] = f"Server '{name}' created"

            elif state == 'absent':
                if existing:
                    self.delete_server(existing['uuid'])
                    result['changed'] = True
                    result['msg'] = f"Server '{name}' deleted"
                else:
                    result['msg'] = f"Server '{name}' does not exist"

        except CoolifyError as e:
            result['failed'] = True
            result['msg'] = str(e)

        return result

    def ensure_project(self, name, state='present', **kwargs):
        """
        Ensure a project exists or is absent (idempotent).

        Args:
            name: Project name
            state: 'present' or 'absent'
            **kwargs: Additional project settings

        Returns:
            dict: Result with 'changed', 'msg', and 'data' keys
        """
        result = {'changed': False, 'msg': '', 'data': None}

        try:
            projects = self.list_projects()
            existing = None
            for project in projects:
                if project.get('name') == name:
                    existing = project
                    break

            if state == 'present':
                if existing:
                    result['msg'] = f"Project '{name}' already exists"
                    result['data'] = existing
                else:
                    result['data'] = self.create_project(name=name, **kwargs)
                    result['changed'] = True
                    result['msg'] = f"Project '{name}' created"

            elif state == 'absent':
                if existing:
                    self.delete_project(existing['uuid'])
                    result['changed'] = True
                    result['msg'] = f"Project '{name}' deleted"
                else:
                    result['msg'] = f"Project '{name}' does not exist"

        except CoolifyError as e:
            result['failed'] = True
            result['msg'] = str(e)

        return result


# Convenience function for creating clients
def create_client(base_url, api_token, **kwargs):
    """
    Factory function to create a Coolify client.

    Args:
        base_url: Coolify API base URL
        api_token: API Bearer token
        **kwargs: Additional client options

    Returns:
        CoolifyClient: Configured client instance
    """
    return CoolifyClient(
        base_url=base_url,
        api_token=api_token,
        **kwargs
    )
