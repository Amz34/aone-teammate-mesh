# System Failure Modes & Operational Safeguards

This document outlines structural operational limits, failure behavior, and mitigation safeguards for `aone-teammate-mesh`.

---

## 1. Failure Modes Matrix

| Failure Mode | Root Cause | System Behavior | Detection Metric | Automated Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| **Database Lock Contention** | Excessive concurrent process writes competing for SQLite database write lock. | SQLite raises `sqlite3.OperationalError: database is locked`. | Write latency > 250ms or retry count exhausted. | Configured `busy_timeout = 5000ms` and WAL mode enabling non-blocking concurrent readers. Exponential backoff retry loop on writes. |
| **Orphaned Handoff Deadlock** | Agent initiates peer handoff, but target peer daemon is offline or crashes prior to receipt. | Handoff record remains in `PENDING` state indefinitely. | Time-to-resolution on `handoff_records` exceeding SLA (default 15m). | Heartbeat monitoring flags unresponsive peers; watchdog re-queues task or elevates to human escalation queue. |
| **Unbounded Workspace Growth** | Teammate persists extensive build artifacts or scratch data within assigned workspace. | Disk partition exhaustion. | Workspace directory size quota check. | Workspace retention policy trims transient files older than 7 days while preserving durable task logs. |
| **Rogue Escalation Flooding** | Failing agent repeatedly raises escalations in a tight failure loop. | Human operator approval queue saturated. | Escalation count per agent > 5 within 10 minutes. | Rate-limiting circuit breaker freezes offending agent in `SUSPENDED` state and sends alert to supervisor. |

---

## 2. Hard Boundaries & Constraints

1. **Host Isolation**: By default, workspaces operate within isolated subdirectories under `~/.aone_teammate_mesh/workspaces/<agent_id>`.
2. **Approval Gate Timeout**: Pending escalations waiting on human approval default to non-destructive pause until explicit operator acknowledgment.
3. **Payload Sanitization**: Payloads exchanged during peer handoffs are serialized via standard JSON to prevent arbitrary bytecode execution.
