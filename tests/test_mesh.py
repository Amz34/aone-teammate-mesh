#!/usr/bin/env python3
"""
Test suite for AOne Teammate Mesh
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Set temp environment directory for testing isolation
temp_dir = tempfile.TemporaryDirectory()
os.environ["AONE_MESH_DIR"] = temp_dir.name

from aone_teammate_mesh.sdk import TeammateMesh, Teammate
from aone_teammate_mesh.engine import get_db, init_mesh_db, WORKSPACES_DIR

class TestAOneTeammateMesh(unittest.TestCase):

    def setUp(self):
        init_mesh_db()
        self.mesh = TeammateMesh()

    def test_01_registration(self):
        tm = self.mesh.get_or_create(
            id="sre_bot",
            name="SRE Bot",
            role="Reliability Worker",
            brief="Maintains zero downtime",
            capabilities=["health_check"]
        )
        self.assertEqual(tm.id, "sre_bot")
        self.assertEqual(tm.role, "Reliability Worker")

    def test_02_task_and_workspace(self):
        tm = self.mesh.get("sre_bot")
        res = tm.run("Execute health check on local services")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertTrue(tm.workspace.exists())

    def test_03_persistent_memory(self):
        tm = self.mesh.get("sre_bot")
        tm.remember("uptime_ratio", 0.9999)
        
        # Cold reload
        reloaded = Teammate("sre_bot")
        self.assertEqual(reloaded.memory["uptime_ratio"], 0.9999)

    def test_04_peer_handoff(self):
        tm1 = self.mesh.get("sre_bot")
        tm2 = self.mesh.get_or_create("qa_bot", "QA Bot", "Auditor", "Audits code")
        h_id = tm1.handoff_to("qa_bot", {"audit_flag": True}, "Run regression suite")
        self.assertTrue(h_id.startswith("hoff_"))

    def test_05_escalation(self):
        tm = self.mesh.get("sre_bot")
        esc_id = tm.escalate("Port in use", "Kill rogue process")
        self.assertTrue(esc_id.startswith("esc_"))
        self.assertEqual(tm.status, "WAITING_APPROVAL")

if __name__ == "__main__":
    unittest.main()
