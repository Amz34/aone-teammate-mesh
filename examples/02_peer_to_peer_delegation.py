#!/usr/bin/env python3
"""
Example 02: Peer-to-Peer Delegation
Demonstrates autonomous collaboration and context handoff between specialized teammates.
"""

from aone_teammate_mesh.sdk import TeammateMesh

def main():
    mesh = TeammateMesh()

    scout = mesh.get_or_create(
        id="lead_scout",
        name="Lead Scout",
        role="Enterprise Lead Discovery Agent",
        brief="Extracts and scores RFPs and consulting opportunities."
    )

    analyst = mesh.get_or_create(
        id="proposal_writer",
        name="Proposal Writer",
        role="RFP Response Architect",
        brief="Drafts technical architecture proposals for qualified enterprise leads."
    )

    # Scout finds a high-tier prospect
    prospect = {
        "client": "Apex Logistics Global",
        "budget_usd": 150000,
        "scope": "Multi-agent autonomous dispatch mesh"
    }

    # Autonomous handoff to proposal writer
    handoff_id = scout.handoff_to(
        target_teammate_id="proposal_writer",
        context=prospect,
        task_title="Draft Solution Architecture Blueprint for Apex Logistics"
    )

    print(f"Handoff generated: {handoff_id}")
    print(f"Scout delegated to {analyst.name} with context keys: {list(prospect.keys())}")

if __name__ == "__main__":
    main()
