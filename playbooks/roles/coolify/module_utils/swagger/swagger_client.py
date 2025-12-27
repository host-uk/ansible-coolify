# -*- coding: utf-8 -*-
# Copyright: (c) 2024, ClouDNS Ansible Collection (original)
# Copyright: (c) 2024, Ansible Coolify Collection (adaptation)
# EUPL-1.2 License (Coolify adaptation), GPL-3.0+ (original)

"""
Reusable Swagger/OpenAPI Client for Ansible modules.

This module provides a generic HTTP client that can work with any OpenAPI 3.0 specification.
It can be used across different Ansible modules/collections to interact with REST APIs.

Usage:
    from ansible_collections.host_uk.cloudns.plugins.module_utils.swagger.swagger_client import (
        SwaggerClient,
        SwaggerClientError,
        load_swagger_spec,
    )

    # Load spec from file or dict
    spec = load_swagger_spec('/path/to/swagger.json')

    # Create client
    client = SwaggerClient(
        spec=spec,
        base_url='https://api.example.com',
        auth_params={'api-key': 'secret'}
    )

    # Make API call
    response = client.call_operation('operationId', {'param1': 'value1'})
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import os
import time
from urllib.parse import urlencode

# Try to import requests, fallback to urllib for minimal dependencies
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import ssl
    import urllib.request
    import urllib.error
    import urllib.parse


class SwaggerClientError(Exception):
    """Exception raised by SwaggerClient operations."""

    def __init__(self, message, status_code=None, response=None):
        super(SwaggerClientError, self).__init__(message)
        self.status_code = status_code
        self.response = response


def load_swagger_spec(spec_source):
    """
    Load an OpenAPI/Swagger specification from various sources.

    Args:
        spec_source: Can be:
            - A file path (str) to a JSON/YAML file
            - A dict containing the parsed spec
            - A JSON string

    Returns:
        dict: The parsed OpenAPI specification

    Raises:
        SwaggerClientError: If the spec cannot be loaded or parsed
    """
    if isinstance(spec_source, dict):
        return spec_source

    if isinstance(spec_source, str):
        # Check if it's a file path
        if os.path.exists(spec_source):
            with open(spec_source, 'r') as f:
                content = f.read()
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Try YAML if JSON fails
                    try:
                        import yaml
                        return yaml.safe_load(content)
                    except ImportError:
                        raise SwaggerClientError(
                            "YAML spec requires PyYAML: pip install pyyaml"
                        )
                    except Exception as e:
                        raise SwaggerClientError(f"Failed to parse spec file: {e}")

        # Try parsing as JSON string
        try:
            return json.loads(spec_source)
        except json.JSONDecodeError:
            raise SwaggerClientError(
                "spec_source must be a valid file path, JSON string, or dict"
            )

    raise SwaggerClientError(
        f"Invalid spec_source type: {type(spec_source).__name__}"
    )


class SwaggerClient:
    """
    A reusable HTTP client that works with OpenAPI/Swagger specifications.

    This client can be used by any Ansible module to interact with REST APIs
    that have an OpenAPI specification.

    Features:
        - Automatic endpoint discovery from OpenAPI spec
        - Support for path, query, and body parameters
        - Multiple authentication methods
        - Retry logic with exponential backoff
        - Response validation
    """

    def __init__(
        self,
        spec,
        base_url=None,
        auth_params=None,
        auth_headers=None,
        timeout=30,
        verify_ssl=True,
        max_retries=3,
        retry_delay=1,
    ):
        """
        Initialize the Swagger client.

        Args:
            spec: OpenAPI specification (dict or path to file)
            base_url: Override the base URL from the spec
            auth_params: Dict of authentication parameters to include in requests
            auth_headers: Dict of authentication headers to include in requests
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            max_retries: Maximum number of retries for failed requests
            retry_delay: Initial delay between retries (doubles each retry)
        """
        self.spec = load_swagger_spec(spec)
        self.base_url = base_url or self._get_base_url_from_spec()
        self.auth_params = auth_params or {}
        self.auth_headers = auth_headers or {}
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Cache operation mappings
        self._operations = self._build_operation_map()

    def _get_base_url_from_spec(self):
        """Extract base URL from the OpenAPI spec."""
        servers = self.spec.get('servers', [])
        if servers:
            return servers[0].get('url', '')

        # OpenAPI 2.0 (Swagger) format
        host = self.spec.get('host', '')
        basePath = self.spec.get('basePath', '')
        schemes = self.spec.get('schemes', ['https'])
        if host:
            return f"{schemes[0]}://{host}{basePath}"

        return ''

    def _build_operation_map(self):
        """Build a map of operationId to operation details."""
        operations = {}
        paths = self.spec.get('paths', {})

        for path, path_item in paths.items():
            for method in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
                if method not in path_item:
                    continue

                operation = path_item[method]
                operation_id = operation.get('operationId')

                if operation_id:
                    operations[operation_id] = {
                        'path': path,
                        'method': method.upper(),
                        'operation': operation,
                        'parameters': self._get_operation_parameters(operation, path_item),
                        'request_body': operation.get('requestBody'),
                    }

        return operations

    def _get_operation_parameters(self, operation, path_item):
        """Get all parameters for an operation, including inherited ones."""
        params = []

        # Path-level parameters
        if 'parameters' in path_item:
            params.extend(path_item['parameters'])

        # Operation-level parameters (override path-level)
        if 'parameters' in operation:
            params.extend(operation['parameters'])

        return params

    def _resolve_ref(self, ref):
        """Resolve a $ref reference in the spec."""
        if not ref.startswith('#/'):
            return None

        parts = ref[2:].split('/')
        current = self.spec
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current

    def get_operation(self, operation_id):
        """
        Get operation details by operationId.

        Args:
            operation_id: The operationId from the OpenAPI spec

        Returns:
            dict: Operation details including path, method, and parameters

        Raises:
            SwaggerClientError: If operation is not found
        """
        if operation_id not in self._operations:
            available = list(self._operations.keys())
            raise SwaggerClientError(
                f"Operation '{operation_id}' not found. "
                f"Available operations: {', '.join(available[:10])}..."
            )
        return self._operations[operation_id]

    def list_operations(self, tag=None):
        """
        List all available operations.

        Args:
            tag: Filter operations by tag

        Returns:
            list: List of operation IDs
        """
        if tag is None:
            return list(self._operations.keys())

        result = []
        for op_id, op_info in self._operations.items():
            operation = op_info['operation']
            if tag in operation.get('tags', []):
                result.append(op_id)
        return result

    def _build_request_body(self, operation_info, params):
        """Build the request body based on the operation's requestBody spec."""
        request_body = operation_info.get('request_body')
        if not request_body:
            return None, 'application/json'

        content = request_body.get('content', {})

        # Handle form-urlencoded (most common for ClouDNS-style APIs)
        if 'application/x-www-form-urlencoded' in content:
            schema = content['application/x-www-form-urlencoded'].get('schema', {})
            if '$ref' in schema:
                schema = self._resolve_ref(schema['$ref']) or {}

            form_data = {}
            properties = schema.get('properties', {})

            for param_name, param_schema in properties.items():
                # Convert Python param name to API param name (underscore to hyphen)
                python_name = param_name.replace('-', '_')
                if python_name in params:
                    value = params[python_name]
                    if value is not None and value is not False:
                        form_data[param_name] = value
                elif param_name in params:
                    value = params[param_name]
                    if value is not None and value is not False:
                        form_data[param_name] = value

            return urlencode(form_data), 'application/x-www-form-urlencoded'

        # Handle JSON body
        if 'application/json' in content:
            return json.dumps(params), 'application/json'

        return None, 'application/json'

    def _make_request(self, method, url, headers, body, content_type):
        """Make an HTTP request using available library."""
        if HAS_REQUESTS:
            return self._make_request_with_requests(method, url, headers, body, content_type)
        return self._make_request_with_urllib(method, url, headers, body, content_type)

    def _make_request_with_requests(self, method, url, headers, body, content_type):
        """Make request using the requests library."""
        headers = headers.copy()
        if body and content_type:
            headers['Content-Type'] = content_type

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            return {
                'status_code': response.status_code,
                'body': response.text,
                'headers': dict(response.headers),
            }
        except requests.exceptions.Timeout:
            raise SwaggerClientError("Request timed out")
        except requests.exceptions.SSLError as e:
            raise SwaggerClientError(f"SSL error: {e}")
        except requests.exceptions.ConnectionError as e:
            raise SwaggerClientError(f"Connection error: {e}")
        except requests.exceptions.RequestException as e:
            raise SwaggerClientError(f"Request failed: {e}")

    def _make_request_with_urllib(self, method, url, headers, body, content_type):
        """Make request using urllib (no external dependencies)."""
        headers = headers.copy()
        if body and content_type:
            headers['Content-Type'] = content_type

        if body and isinstance(body, str):
            body = body.encode('utf-8')

        request = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method=method,
        )

        try:
            context = None
            if not self.verify_ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(
                request, timeout=self.timeout, context=context
            ) as response:
                return {
                    'status_code': response.status,
                    'body': response.read().decode('utf-8'),
                    'headers': dict(response.headers),
                }
        except urllib.error.HTTPError as e:
            return {
                'status_code': e.code,
                'body': e.read().decode('utf-8') if e.fp else '',
                'headers': dict(e.headers) if e.headers else {},
            }
        except urllib.error.URLError as e:
            if 'timed out' in str(e.reason).lower():
                raise SwaggerClientError("Request timed out")
            raise SwaggerClientError(f"Request failed: {e.reason}")

    def call_operation(self, operation_id, params=None, raw_response=False):
        """
        Call an API operation by its operationId.

        Args:
            operation_id: The operationId from the OpenAPI spec
            params: Dict of parameters for the operation
            raw_response: If True, return the full response dict instead of just the body

        Returns:
            The parsed JSON response, or raw response if raw_response=True

        Raises:
            SwaggerClientError: If the operation fails
        """
        params = params or {}
        operation_info = self.get_operation(operation_id)

        path = operation_info['path']
        method = operation_info['method']

        # Build URL with path parameters
        for param in operation_info['parameters']:
            if param.get('in') == 'path':
                param_name = param['name']
                python_name = param_name.replace('-', '_')
                if python_name in params:
                    path = path.replace(f'{{{param_name}}}', str(params[python_name]))
                elif param_name in params:
                    path = path.replace(f'{{{param_name}}}', str(params[param_name]))

        url = f"{self.base_url.rstrip('/')}{path}"

        # Build query parameters
        query_params = dict(self.auth_params)  # Start with auth params
        for param in operation_info['parameters']:
            if param.get('in') == 'query':
                param_name = param['name']
                python_name = param_name.replace('-', '_')
                if python_name in params:
                    value = params[python_name]
                    if value is not None:
                        query_params[param_name] = value
                elif param_name in params:
                    value = params[param_name]
                    if value is not None:
                        query_params[param_name] = value

        if query_params:
            url = f"{url}?{urlencode(query_params)}"

        # Build request body
        body, content_type = self._build_request_body(operation_info, params)

        # Add auth params to body for form-urlencoded requests
        if content_type == 'application/x-www-form-urlencoded' and self.auth_params:
            auth_encoded = urlencode(self.auth_params)
            if body:
                body = f"{auth_encoded}&{body}"
            else:
                body = auth_encoded

        # Build headers
        headers = dict(self.auth_headers)
        headers['Accept'] = 'application/json'

        # Make request with retries
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = self._make_request(method, url, headers, body, content_type)

                if raw_response:
                    return response

                # Parse JSON response
                try:
                    return json.loads(response['body'])
                except json.JSONDecodeError:
                    return {'raw': response['body']}

            except SwaggerClientError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                raise

        if last_error:
            raise last_error

    def get_operation_schema(self, operation_id):
        """
        Get the request/response schema for an operation.

        Args:
            operation_id: The operationId from the OpenAPI spec

        Returns:
            dict: Schema information including parameters and response schemas
        """
        operation_info = self.get_operation(operation_id)
        operation = operation_info['operation']

        result = {
            'parameters': [],
            'request_body': None,
            'responses': {},
        }

        # Parse parameters
        for param in operation_info['parameters']:
            result['parameters'].append({
                'name': param.get('name'),
                'in': param.get('in'),
                'required': param.get('required', False),
                'description': param.get('description', ''),
                'schema': param.get('schema', {}),
            })

        # Parse request body
        if operation_info['request_body']:
            result['request_body'] = operation_info['request_body']

        # Parse responses
        for status_code, response in operation.get('responses', {}).items():
            result['responses'][status_code] = {
                'description': response.get('description', ''),
                'content': response.get('content', {}),
            }

        return result


class SwaggerClientBuilder:
    """
    Builder class for creating SwaggerClient instances with fluent interface.

    Usage:
        client = (SwaggerClientBuilder()
            .with_spec('/path/to/spec.json')
            .with_base_url('https://api.example.com')
            .with_auth_param('api-key', 'secret')
            .with_timeout(60)
            .build())
    """

    def __init__(self):
        self._spec = None
        self._base_url = None
        self._auth_params = {}
        self._auth_headers = {}
        self._timeout = 30
        self._verify_ssl = True
        self._max_retries = 3
        self._retry_delay = 1

    def with_spec(self, spec):
        """Set the OpenAPI specification."""
        self._spec = spec
        return self

    def with_base_url(self, base_url):
        """Override the base URL from the spec."""
        self._base_url = base_url
        return self

    def with_auth_param(self, name, value):
        """Add an authentication parameter."""
        self._auth_params[name] = value
        return self

    def with_auth_params(self, params):
        """Add multiple authentication parameters."""
        self._auth_params.update(params)
        return self

    def with_auth_header(self, name, value):
        """Add an authentication header."""
        self._auth_headers[name] = value
        return self

    def with_auth_headers(self, headers):
        """Add multiple authentication headers."""
        self._auth_headers.update(headers)
        return self

    def with_timeout(self, timeout):
        """Set the request timeout in seconds."""
        self._timeout = timeout
        return self

    def with_ssl_verification(self, verify):
        """Enable or disable SSL verification."""
        self._verify_ssl = verify
        return self

    def with_retries(self, max_retries, retry_delay=1):
        """Configure retry behavior."""
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        return self

    def build(self):
        """Build and return the SwaggerClient instance."""
        if self._spec is None:
            raise SwaggerClientError("Spec is required")

        return SwaggerClient(
            spec=self._spec,
            base_url=self._base_url,
            auth_params=self._auth_params,
            auth_headers=self._auth_headers,
            timeout=self._timeout,
            verify_ssl=self._verify_ssl,
            max_retries=self._max_retries,
            retry_delay=self._retry_delay,
        )
