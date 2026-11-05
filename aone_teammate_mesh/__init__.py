"""
AOne Teammate Mesh Package
Autonomous Persistent AI Coworker Runtime & Mesh.
"""

from .engine import init_mesh_db, TeammateRuntime, notify_telegram
from .sdk import Teammate, TeammateMesh

__version__ = "0.1.0"
__all__ = ["init_mesh_db", "TeammateRuntime", "notify_telegram", "Teammate", "TeammateMesh"]
