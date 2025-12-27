#!/bin/bash
# Master test runner for Docker development environment
# Usage: ./run_all_tests.sh [quick|full|api|module]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$TEST_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test result counters
PASSED=0
FAILED=0
SKIPPED=0
TOTAL_TIME=0

# Test mode
MODE="${1:-quick}"

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_header() { echo -e "\n${BLUE}========================================${NC}"; echo -e "${BLUE}$1${NC}"; echo -e "${BLUE}========================================${NC}"; }

run_test() {
    local test_name=$1
    local test_file=$2
    local start_time
    local end_time
    local duration

    log_header "Running: $test_name"
    start_time=$(date +%s)

    if ansible-playbook -i "$PROJECT_ROOT/inventory/" "$test_file" -v; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        TOTAL_TIME=$((TOTAL_TIME + duration))
        log_info "PASSED: $test_name (${duration}s)"
        ((PASSED++))
        return 0
    else
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        TOTAL_TIME=$((TOTAL_TIME + duration))
        log_error "FAILED: $test_name (${duration}s)"
        ((FAILED++))
        return 1
    fi
}

cleanup() {
    log_info "Running cleanup..."
    cd "$PROJECT_ROOT"

    # Clean up test environment
    docker compose -f ./docker-test/docker-compose.yml down -v 2>/dev/null || true
    rm -rf ./docker-test ./docker-test-logs 2>/dev/null || true

    # Clean up test SSH keys (only test-* prefixed ones)
    rm -f ~/.ssh/test-*.lan ~/.ssh/test-*.lan.pub 2>/dev/null || true

    log_info "Cleanup complete"
}

show_usage() {
    echo "Usage: $0 [mode]"
    echo ""
    echo "Modes:"
    echo "  quick   - Run container, SSH, and Makefile tests (default)"
    echo "  full    - Run all tests including Coolify deployment"
    echo "  api     - Run API-related tests only"
    echo "  module  - Run module tests only"
    echo ""
    echo "Examples:"
    echo "  $0           # Run quick tests"
    echo "  $0 full      # Run full test suite"
    echo "  $0 api       # Run API tests only"
}

# Validate prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v docker &>/dev/null; then
        log_error "Docker not found"
        exit 1
    fi

    if ! command -v ansible-playbook &>/dev/null; then
        log_error "Ansible not found"
        exit 1
    fi

    if ! docker info &>/dev/null; then
        log_error "Docker daemon not running"
        exit 1
    fi

    log_info "All prerequisites met"
}

# Print summary
print_summary() {
    log_header "TEST SUMMARY"
    echo -e "${GREEN}Passed:${NC}  $PASSED"
    echo -e "${RED}Failed:${NC}  $FAILED"
    echo -e "${YELLOW}Skipped:${NC} $SKIPPED"
    echo -e "${BLUE}Total time:${NC} ${TOTAL_TIME}s"
    echo ""

    if [[ $FAILED -gt 0 ]]; then
        log_error "Some tests failed!"
        return 1
    else
        log_info "All tests passed!"
        return 0
    fi
}

# Main execution
main() {
    local exit_code=0

    log_header "Docker Dev Test Suite - Mode: $MODE"

    check_prerequisites

    # Trap for cleanup on exit
    trap cleanup EXIT

    case "$MODE" in
        quick)
            run_test "Container Lifecycle" "$TEST_DIR/test_01_container_lifecycle.yml" || exit_code=1
            run_test "SSH Connectivity" "$TEST_DIR/test_02_ssh_connectivity.yml" || exit_code=1
            run_test "Makefile Targets" "$TEST_DIR/test_03_makefile_targets.yml" || exit_code=1
            ;;
        full)
            run_test "Container Lifecycle" "$TEST_DIR/test_01_container_lifecycle.yml" || exit_code=1
            run_test "SSH Connectivity" "$TEST_DIR/test_02_ssh_connectivity.yml" || exit_code=1
            run_test "Makefile Targets" "$TEST_DIR/test_03_makefile_targets.yml" || exit_code=1
            run_test "Coolify Installation" "$TEST_DIR/test_04_coolify_install.yml" || exit_code=1
            run_test "API Setup" "$TEST_DIR/test_05_api_setup.yml" || exit_code=1
            run_test "Node Registration" "$TEST_DIR/test_06_node_registration.yml" || exit_code=1
            run_test "Full Integration" "$TEST_DIR/test_07_full_integration.yml" || exit_code=1
            ;;
        api)
            run_test "API Setup" "$TEST_DIR/test_05_api_setup.yml" || exit_code=1
            run_test "Node Registration" "$TEST_DIR/test_06_node_registration.yml" || exit_code=1
            ;;
        module)
            # Module tests - add as modules are implemented
            if [[ -f "$TEST_DIR/../modules/test_coolify_private_key.yml" ]]; then
                run_test "Private Key Module" "$TEST_DIR/../modules/test_coolify_private_key.yml" || exit_code=1
            fi
            if [[ -f "$TEST_DIR/../modules/test_coolify_project.yml" ]]; then
                run_test "Project Module" "$TEST_DIR/../modules/test_coolify_project.yml" || exit_code=1
            fi
            ;;
        -h|--help|help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown mode: $MODE"
            show_usage
            exit 1
            ;;
    esac

    print_summary || exit_code=1

    exit $exit_code
}

main "$@"
