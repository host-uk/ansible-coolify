# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Coolify Collection
# EUPL-1.2 License

"""
Swagger/OpenAPI utilities for Coolify Ansible modules.

This package provides reusable components for interacting with the Coolify API
using its OpenAPI specification.

Components:
    - swagger_client: Generic OpenAPI client (reusable for any API)
    - coolify_api: Coolify-specific API client

Usage:
    from ansible_collections.coolify.plugins.module_utils.swagger.coolify_api import (
        CoolifyClient,
        CoolifyError,
    )

    # For generic Swagger/OpenAPI
    from ansible_collections.coolify.plugins.module_utils.swagger.swagger_client import (
        SwaggerClient,
        SwaggerClientBuilder,
        load_swagger_spec,
    )
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type
