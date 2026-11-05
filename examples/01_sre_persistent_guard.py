#!/usr/bin/env python3
"""
Example 01: SRE Persistent Guard
Demonstrates creating a persistent digital colleague that retains memory across invocations.
"""

from aone_teammate_mesh.sdk import TeammateMesh

def main():
    mesh = TeammateMesh()

    # Provision persistent SRE Teammate
    sre = mesh.get_or_create(
        id="sre_guard",
        name="SRE Guard",
        role="Autonomous Site Reliability Engineer",
        brief="Monitors server swap, memory containment, and ports.",
        capabilities=["telemetry", "self_healing"]
    )

    print(f"Loaded Teammate: {sre.name} ({sre.role})")
    print(f"Workspace path: {sre.workspace}")

    # Run autonomous task
    res = sre.run("Check system memory ceiling and report swap utilization")
    print("Execution output:", res["output"])

    # Persist context in cross-session memory
    sre.remember("last_swap_utilization_pct", 14.2)
    print("Updated Memory Keys:", list(sre.memory.keys()))

if __name__ == "__main__":
    main()
