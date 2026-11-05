#!/usr/bin/env python3
"""
AOne Teammate Mesh Unified CLI
Manage persistent AI coworkers, isolated workspaces, peer handoffs, and HITL gates.
"""

import os
import sys
import json
import argparse
from pathlib import Path

from .sdk import TeammateMesh, Teammate
from .engine import init_mesh_db, get_db

def cmd_list(args):
    mesh = TeammateMesh()
    teammates = mesh.list_all()
    if not teammates:
        print("No teammates currently registered. Use 'aone-teammate register' or seed default team.")
        return
    print(f"\n{'ID':<18} | {'NAME':<24} | {'ROLE':<34} | {'STATUS':<12}")
    print("-" * 94)
    for t in teammates:
        print(f"{t['id']:<18} | {t['name']:<24} | {t['role']:<34} | {t['status']:<12}")
    print()

def cmd_register(args):
    mesh = TeammateMesh()
    caps = [c.strip() for c in args.caps.split(",")] if args.caps else ["general_execution"]
    tm = mesh.register(
        teammate_id=args.id,
        name=args.name,
        role=args.role,
        brief=args.brief,
        capabilities=caps
    )
    print(f"✅ Successfully registered Teammate: {tm.name} [{tm.id}] as '{tm.role}'")

def cmd_run(args):
    mesh = TeammateMesh()
    tm = mesh.get(args.id)
    if not tm:
        print(f"❌ Error: Teammate '{args.id}' not found.")
        sys.exit(1)
    print(f"🚀 Dispatching goal to {tm.name} ({tm.role})...")
    res = tm.run(args.goal, priority=args.priority)
    print(f"✨ Result: {res['output']}")
    print(f"📁 Workspace: {res['workspace']}")

def cmd_handoff(args):
    mesh = TeammateMesh()
    tm = mesh.get(args.from_id)
    if not tm:
        print(f"❌ Error: Origin teammate '{args.from_id}' not found.")
        sys.exit(1)
    
    ctx = {}
    if args.context:
        try:
            ctx = json.loads(args.context)
        except Exception as e:
            ctx = {"raw": args.context}
            
    h_id = tm.handoff_to(args.to_id, ctx, args.task)
    print(f"🤝 Handoff recorded: {h_id} (Delivered from '{args.from_id}' to '{args.to_id}')")

def cmd_escalate(args):
    mesh = TeammateMesh()
    tm = mesh.get(args.id)
    if not tm:
        print(f"❌ Error: Teammate '{args.id}' not found.")
        sys.exit(1)
    esc_id = tm.escalate(args.blocker, args.action)
    print(f"🚨 Escalation gate triggered: {esc_id}")

def cmd_status(args):
    mesh = TeammateMesh()
    if args.id:
        tm = mesh.get(args.id)
        if not tm:
            print(f"❌ Error: Teammate '{args.id}' not found.")
            sys.exit(1)
        print(f"\n=== Teammate Profile: {tm.name} ===")
        print(f"ID:           {tm.id}")
        print(f"Role:         {tm.role}")
        print(f"Status:       {tm.status}")
        print(f"Brief:        {tm.brief}")
        print(f"Workspace:    {tm.workspace}")
        print(f"Memory Keys:  {list(tm.memory.keys())}")
        
        with get_db() as conn:
            tasks = conn.execute("SELECT id, title, priority, status, created_at FROM tasks WHERE teammate_id = ? ORDER BY created_at DESC LIMIT 5", (tm.id,)).fetchall()
            if tasks:
                print("\nRecent Tasks:")
                for task in tasks:
                    print(f"  [{task['status']}] {task['id']} - {task['title']} ({task['created_at']})")
        print()
    else:
        cmd_list(args)

def cmd_seed(args):
    """Seeds standard core enterprise teammates"""
    mesh = TeammateMesh()
    defaults = [
        {
            "id": "sre_sentinel",
            "name": "SRE Sentinel",
            "role": "Autonomous Infra & Capacity Guard",
            "brief": "Monitors host memory, swap headroom, port bindings, and auto-heals leaks.",
            "capabilities": ["system_telemetry", "self_healing", "telegram_dispatch", "port_guard"]
        },
        {
            "id": "lead_scout",
            "name": "Market & Lead Scout",
            "role": "Consultancy & Enterprise Lead Finder",
            "brief": "Extracts high-value client consulting and corporate RFP leads across public channels.",
            "capabilities": ["data_extraction", "scoring", "telegram_alerting", "deduplication"]
        },
        {
            "id": "code_auditor",
            "name": "Codebase & QA Auditor",
            "role": "Quality Assurance & Compliance Reviewer",
            "brief": "Executes clean-room audits, architectural reviews, linting gates, and test suites.",
            "capabilities": ["ast_analysis", "test_execution", "gate_enforcement", "report_generation"]
        },
        {
            "id": "research_analyst",
            "name": "Deep Research Analyst",
            "role": "Technical Research & Competitive Intelligence",
            "brief": "Synthesizes multi-source research briefs, open-source architectures, and whitepapers.",
            "capabilities": ["web_search", "academic_retrieval", "synthesis", "whitepaper_drafting"]
        }
    ]
    for d in defaults:
        mesh.register(d["id"], d["name"], d["role"], d["brief"], d["capabilities"])
    print(f"✅ Successfully seeded {len(defaults)} core enterprise teammates!")

def main():
    init_mesh_db()
    parser = argparse.ArgumentParser(description="AOne Teammate Mesh Unified CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List all registered teammates")
    subparsers.add_parser("seed", help="Seed default enterprise teammates")

    reg_parser = subparsers.add_parser("register", help="Register a persistent teammate")
    reg_parser.add_argument("id", help="Unique identifier (e.g. sre_sentinel)")
    reg_parser.add_argument("--name", required=True, help="Display name")
    reg_parser.add_argument("--role", required=True, help="Teammate operational role")
    reg_parser.add_argument("--brief", required=True, help="Core mission brief and standing instructions")
    reg_parser.add_argument("--caps", help="Comma-separated capability tags")

    run_parser = subparsers.add_parser("run", help="Dispatch an autonomous task to a teammate")
    run_parser.add_argument("id", help="Teammate ID")
    run_parser.add_argument("goal", help="Task goal/instruction")
    run_parser.add_argument("--priority", default="NORMAL", choices=["LOW", "NORMAL", "HIGH", "CRITICAL"])

    ho_parser = subparsers.add_parser("handoff", help="Peer-to-peer delegation between teammates")
    ho_parser.add_argument("from_id", help="Origin teammate ID")
    ho_parser.add_argument("to_id", help="Target teammate ID")
    ho_parser.add_argument("task", help="Delegated task title")
    ho_parser.add_argument("--context", help="JSON serialized context payload")

    esc_parser = subparsers.add_parser("escalate", help="Trigger Human-in-the-loop escalation")
    esc_parser.add_argument("id", help="Teammate ID")
    esc_parser.add_argument("blocker", help="Description of roadblock")
    esc_parser.add_argument("action", help="Suggested human action")

    status_parser = subparsers.add_parser("status", help="Inspect teammate state and memory")
    status_parser.add_argument("id", nargs="?", help="Optional Teammate ID")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "list": cmd_list,
        "seed": cmd_seed,
        "register": cmd_register,
        "run": cmd_run,
        "handoff": cmd_handoff,
        "escalate": cmd_escalate,
        "status": cmd_status
    }
    dispatch[args.command](args)

if __name__ == "__main__":
    main()
