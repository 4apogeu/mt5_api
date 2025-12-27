# AGENTS

<skills_system priority="1">

## Available Skills

<!-- SKILLS_TABLE_START -->
<usage>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively. Skills provide specialized capabilities and domain knowledge.

How to use skills:
- Invoke: Bash("openskills read <skill-name>")
- The skill content will load with detailed instructions on how to complete the task
- Base directory provided in output for resolving bundled resources (references/, scripts/, assets/)

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
- Each skill invocation is stateless
</usage>

<available_skills>

<skill>
<name>writing-plans</name>
<description>Create detailed implementation plans with bite-sized tasks for engineers with zero codebase context</description>
<location>project</location>
</skill>

</available_skills>
<!-- SKILLS_TABLE_END -->

</skills_system>
@../../ai/systems/SOFT-DEV-PRIN.md

# Agent Memory & Knowledge Strategy

You are an AI Agent equipped with two types of memory. You MUST follow these rules whenever a user provides a piece of information that should be "remembered."

## 1. Memory Storage Options
When the user shares a fact, preference, or architectural decision, you must categorize it:

### Option A: Local Project Context (`AGENTS.md`)
* **Use for:** Project-specific technical specs, todo lists, active bugs, or folder structures.
* **Scope:** This project only.
* **Action:** Append the info to the "Project Log" section at the bottom of this file.

---

## 3. Project Log (Automated Section)

### 2025-12-27: Python Server Implementation Complete

**Architecture**: Python (TCP Server) ← → MT5 EA (TCP Client)
- MQL5 lacks server sockets, so Python must be the server

**Structure**:
```
mt5_bridge/
├── protocol/       # JSON message models & parsing
├── server/         # TCP server & connection handling
├── trading/        # MT5Bridge high-level API
└── main.py         # Entry point
```

**API Methods**:
- `buy()`, `sell()`, `place_pending_order()`
- `get_rates()`, `get_tick()`
- `get_account()`, `get_positions()`
- `close_position()`, `modify_position()`

**Next**: Implement MT5 EA (MQL5 client)

### 2025-12-27: MT5 EA Implementation Complete

**File**: `mql5/Experts/MT5SocketClient.mq5`

**Features**:
- Socket client connecting to Python server
- OnTimer-based polling (100ms interval)
- JSON message parsing and response building
- All commands: TRADE, GET_DATA, GET_TICK, GET_ACCOUNT, GET_POSITIONS, CLOSE_POSITION, HEARTBEAT

**Setup on MT5**:
1. Copy EA to `MQL5/Experts/` folder
2. Allow WebRequest for Python server IP in Tools > Options > Expert Advisors
3. Attach EA to any chart, configure ServerAddress and ServerPort

**Status**: Ready for testing
