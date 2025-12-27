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

### 2025-12-27: Winsock DLL Migration & Testing Complete

**Issue**: MQL5 native socket functions unreliable
**Solution**: Migrated to Windows Winsock DLL (`ws2_32.dll`)

**Key imports**:
- `WSAStartup`, `WSACleanup`, `WSAGetLastError`
- `socket`, `connect`, `send`, `recv`, `closesocket`
- `ioctlsocket` (non-blocking mode)

**Testing Results**:
- BTCUSD BUY 0.01 lots - SUCCESS
- CLOSE_POSITION - SUCCESS ($0.12 profit)

**All commands verified working**:
- TRADE (BUY/SELL)
- GET_TICK, GET_DATA, GET_ACCOUNT, GET_POSITIONS
- CLOSE_POSITION

---

### 2025-12-27: Order Panel UI Implementation Complete

**Framework**: Tkinter (standard library)

**Structure**:
```
mt5_bridge/ui/
├── __init__.py       # Module exports
├── config.py         # PanelConfig, Colors dataclasses
├── async_bridge.py   # AsyncBridge for Tkinter-asyncio integration
├── widgets.py        # TradeButton, StatusBar, SymbolSelector, VolumeInput
└── order_panel.py    # Main OrderPanel class

run_panel.py          # Standalone runner
```

**Features**:
- B/S/C buttons with keyboard shortcuts (B=Buy, S=Sell, C=Close, Esc=Quit)
- Symbol dropdown (BTCUSD, EURUSD, GBPUSD, USDJPY, XAUUSD)
- Volume input with +/- buttons
- Visual feedback (hover, active, success/error flash)
- Status bar showing connection and last action
- Thread-safe async operations via queue

**Usage**:
```bash
python run_panel.py --symbol BTCUSD --volume 0.01
```

**Status**: Ready for testing

---

### PLANNED: Execution Speed Measurement

**Approach**: Embedded EA timestamps + round-trip calculation

**Timestamp points**:
- T1: Python sends command
- T2: EA receives (`GetMicrosecondCount()`)
- T3: EA executes trade
- T4: Python receives response

**Metrics**:
- Round-trip latency (T4-T1)
- EA processing time (T3-T2)
- Network estimate ((T4-T1)-(T3-T2))/2

**Files to create**:
```
mt5_bridge/timing/
├── models.py      # TimingData, LatencyStats
├── collector.py   # Capture & store timing
├── analyzer.py    # Statistics (avg, P50, P95, P99)
└── reporter.py    # Console/CSV output
```

**EA modification required**:
- Add `GetMicrosecondCount()` in HandleMessage and BuildSuccessResponse
- Include `timing` object in JSON response

**Implementation steps**:
1. Modify EA to capture and return timestamps
2. Update Response model with optional `timing` field
3. Create `timing/collector.py` - TimingCollector class
4. Create `timing/analyzer.py` - LatencyAnalyzer with stats
5. Add `enable_timing` flag to MT5Bridge
6. Create `test_latency.py` - benchmark script
