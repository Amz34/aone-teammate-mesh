#!/usr/bin/env python3
"""
AOne Teammate Mesh Python SDK
Developer interface for defining, running, orchestrating, and observing persistent AI teammates.
"""

import os
import sys
import json
import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from .engine import (
    get_db,
    init_mesh_db,
    TeammateRuntime,
    notify_telegram
)

class Teammate:
    """High-level SDK representation of an autonomous persistent Teammate"""

    def __init__(self, teammate_id: str):
        self.id = teammate_id
        self._runtime = TeammateRuntime(teammate_id)

    @property
    def name(self) -> str:
        return self._runtime.data["name"]

    @property
    def role(self) -> str:
        return self._runtime.data["role"]

    @property
    def brief(self) -> str:
        return self._runtime.data["system_brief"]

    @property
    def status(self) -> str:
        self._runtime.load()
        return self._runtime.data["status"]

    @property
    def memory(self) -> Dict[str, Any]:
        self._runtime.load()
        return self._runtime.memory

    @property
    def workspace(self) -> Path:
        return self._runtime.workspace

    def remember(self, key: str, value: Any):
        self._runtime.save_memory(key, value)

    def run(self, goal: str, priority: str = "NORMAL") -> Dict[str, Any]:
        """Dispatches an autonomous goal to the teammate"""
        task_id = f"task_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(2).hex()}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        with get_db() as conn:
            conn.execute(
                """INSERT INTO tasks (id, teammate_id, title, goal, priority, status, created_at)
                   VALUES (?, ?, ?, ?, ?, 'QUEUED', ?)""",
                (task_id, self.id, goal[:80], goal, priority, now)
            )

        return self._runtime.execute_task(task_id, goal)

    def handoff_to(self, target_teammate_id: str, context: Dict[str, Any], task_title: str) -> str:
        """Peer-to-Peer delegation to another teammate"""
        return self._runtime.handoff_to(target_teammate_id, context, task_title)

    def escalate(self, blocker: str, suggested_action: str) -> str:
        """Escalate to Human-in-the-loop gate"""
        return self._runtime.escalate_blocker(blocker, suggested_action)


class TeammateMesh:
    """Registry and lifecycle manager for all persistent teammates"""

    def __init__(self):
        init_mesh_db()

    def register(self, teammate_id: str, name: str, role: str, brief: str, capabilities: Optional[List[str]] = None) -> Teammate:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        caps_json = json.dumps(capabilities or ["autonomous_execution", "memory_persistence"])
        
        with get_db() as conn:
            conn.execute("""
                INSERT INTO teammates (id, name, role, system_brief, capabilities, status, memory, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'IDLE', '{}', ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    role = excluded.role,
                    system_brief = excluded.system_brief,
                    capabilities = excluded.capabilities,
                    updated_at = excluded.updated_at
            """, (teammate_id, name, role, brief, caps_json, now, now))
        
        return Teammate(teammate_id)

    def get(self, teammate_id: str) -> Optional[Teammate]:
        with get_db() as conn:
            cur = conn.execute("SELECT id FROM teammates WHERE id = ?", (teammate_id,))
            if cur.fetchone():
                return Teammate(teammate_id)
        return None

    def get_or_create(self, id: str, name: str, role: str, brief: str, capabilities: Optional[List[str]] = None) -> Teammate:
        existing = self.get(id)
        if existing:
            return existing
        return self.register(id, name, role, brief, capabilities)

    def list_all(self) -> List[Dict[str, Any]]:
        with get_db() as conn:
            cur = conn.execute("SELECT id, name, role, status, capabilities, updated_at FROM teammates ORDER BY id")
            return [dict(row) for row in cur.fetchall()]

    def list_handoffs(self, limit: int = 10) -> List[Dict[str, Any]]:
        with get_db() as conn:
            cur = conn.execute("SELECT * FROM handoffs ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(row) for row in cur.fetchall()]

    def list_escalations(self, limit: int = 10) -> List[Dict[str, Any]]:
        with get_db() as conn:
            cur = conn.execute("SELECT * FROM escalations ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(row) for row in cur.fetchall()]
