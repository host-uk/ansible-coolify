### Testing Suite

This directory contains automated tests for the project's Ansible roles and playbooks.

#### Available Tests

1.  **Syntax Verification** (`test_coolify_roles_syntax.yml`):
    - Ensures all roles (`common`, `coolify`, `coolify-application`, etc.) can be loaded and their tasks are syntactically correct.
    - Run via: `make test-syntax`

2.  **Logic Testing** (`test_coolify_token.yml`):
    - Verifies the API token extraction logic, including handling of noisy output from PHP tinker.
    - Run via: `make test-logic`

3.  **Parallels VM Lifecycle** (`test_parallels_vm.yml`):
    - Tests the creation, configuration, and startup of Parallels VMs on macOS.
    - Run via: `make test-parallels`

#### Running Tests

You can run the entire suite using:
```bash
make test
```

#### CI/CD Integration

These tests are designed to be run in a CI environment (e.g., GitHub Actions). The `Makefile` provides targets that return non-zero exit codes on failure.
