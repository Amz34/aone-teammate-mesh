#!/usr/bin/env bash
# ==============================================================================
# Enterprise Verification Suite - Frictionless Offline / Mock Verification
# Usage: ./scripts/verify_enterprise.sh [--mock]
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export MOCK_MODE=1
export PYTHONUNBUFFERED=1
export PYTHONPATH="${REPO_ROOT}:${PYTHONPATH:-}"

# Isolate SQLite database in transient mock directory
MOCK_DIR="$(mktemp -d -t aone_mesh_verify_XXXXXX)"
trap 'rm -rf "${MOCK_DIR}"' EXIT
export AONE_MESH_DIR="${MOCK_DIR}"

echo "======================================================================"
echo "⚡ RUNNING ENTERPRISE VERIFICATION SUITE: aone-teammate-mesh"
echo "   Mode: MOCK_MODE=${MOCK_MODE} (Zero Credentials / Offline Verification)"
echo "   Root: ${REPO_ROOT}"
echo "   Temp Store: ${AONE_MESH_DIR}"
echo "======================================================================"

cd "${REPO_ROOT}"

echo ""
echo "[Step 1/3] Running Unit & Integration Test Suite..."
python3 -m unittest tests/test_mesh.py -v

echo ""
echo "[Step 2/3] Validating Autonomous Multi-Agent Handoff & Persistence Workflow..."
python3 -c "
import os
from aone_teammate_mesh.sdk import TeammateMesh

mesh = TeammateMesh()

# 1. Register agents
lead = mesh.get_or_create(
    id='lead_architect',
    name='Lead Architect',
    role='System Architecture',
    brief='Designs fault-tolerant topologies',
    capabilities=['design', 'review']
)
worker = mesh.get_or_create(
    id='qa_specialist',
    name='QA Specialist',
    role='Quality Engineering',
    brief='Executes deterministic audit passes',
    capabilities=['audit', 'regression']
)

# 2. Record state into SQLite WAL
lead.remember('preferred_protocol', 'WAL-SQLite')
lead.remember('max_latency_ms', 1.5)

# 3. Trigger handoff
h_id = lead.handoff_to('qa_specialist', {'target': 'api_gateway', 'mock': True}, 'Verify latency SLA')
assert h_id.startswith('hoff_'), f'Handoff ID expected hoff_ prefix: {h_id}'

# 4. Escalate test
esc_id = worker.escalate('Telemetry anomaly', 'Threshold exceeded mock bounds')
assert esc_id.startswith('esc_'), f'Escalation ID expected esc_ prefix: {esc_id}'
assert worker.status == 'WAITING_APPROVAL'

print(f'✓ Verified Multi-Agent Topology: Handoff={h_id}, Escalation={esc_id}, Status={worker.status}')
"

echo ""
echo "[Step 3/3] Validating SRE Guard Isolated Autonomous Execution..."
python3 examples/01_sre_persistent_guard.py

echo ""
echo "======================================================================"
echo "✅ ENTERPRISE VERIFICATION SUITE PASSED (aone-teammate-mesh)"
echo "======================================================================"
