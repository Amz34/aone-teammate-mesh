#!/usr/bin/env python3
"""
Example 03: Human-In-The-Loop (HITL) Escalation
Demonstrates pausing execution when reaching an obstacle or requiring critical human authorization.
"""

from aone_teammate_mesh.sdk import TeammateMesh

def main():
    mesh = TeammateMesh()

    auditor = mesh.get_or_create(
        id="compliance_bot",
        name="Compliance Auditor",
        role="Security & Access Control Reviewer",
        brief="Audits deployment manifests for privilege escalation risks."
    )

    print(f"Current status: {auditor.status}")

    # Auditor encounters an ambiguous permission grant
    esc_id = auditor.escalate(
        blocker="Detected wildcard admin permission on production cluster",
        suggested_action="Review and approve scoped role binding with security team"
    )

    print(f"Escalation ID: {esc_id}")
    print(f"Teammate transitioned to: {auditor.status}")
    print("Dispatched real-time interactive alert to Telegram Human-in-the-Loop gate.")

if __name__ == "__main__":
    main()
