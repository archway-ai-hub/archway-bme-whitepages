# Swarm - Parallel Multi-Agent Orchestration

Execute complex tasks by decomposing them and running multiple specialized agents in parallel, with MCP tool integration.

## Task to Execute
$ARGUMENTS

## Instructions

You are orchestrating a swarm of specialized agents for a Python-based restaurant lead enrichment tool. Follow this process exactly:

### Step 0: Parse Options

Check if the task includes any flags:
- `--dry-run` or `-d`: Show execution plan without running agents
- `--focus=<phase>`: Only run specific phase (e.g., `--focus=2`)
- `--fast`: Use haiku model for simple subtasks to reduce token usage
- `--no-mcp`: Disable MCP tool usage (agents only)

If `--dry-run` is present, skip to Step 3 and stop after showing the plan.

### MCP Tools Available

The swarm can leverage these MCP tools when beneficial:

#### Code Intelligence
| MCP | Tool | Use For |
|-----|------|---------|
| 🔶 **serena** | `find_symbol`, `get_symbols_overview` | Symbolic code navigation and understanding |
| 🔶 **serena** | `replace_symbol_body`, `insert_after_symbol` | Precise code modifications |
| 🔶 **serena** | `find_referencing_symbols` | Find all usages of a function/class |
| 🟤 **morph-mcp** | `edit_file` | Fast, accurate file editing |
| 🟤 **morph-mcp** | `warpgrep_codebase_search` | Intelligent codebase search |

#### Browser Testing
| MCP | Tool | Use For |
|-----|------|---------|
| 🟢 **playwright** | `browser_navigate`, `browser_snapshot` | E2E testing, UI verification |
| 🔵 **chrome-devtools** | `take_snapshot`, `list_network_requests` | Debug API issues |

#### Problem Solving
| MCP | Tool | Use For |
|-----|------|---------|
| 🟣 **sequential-thinking** | `sequentialthinking` | Complex multi-step reasoning |

**When to use MCPs:**
- 🔍 Complex code search → Use **morph-mcp** warpgrep or **serena** symbols
- ✏️ Precise edits → Use **serena** symbolic editing or **morph-mcp** edit_file
- 🧠 Complex reasoning → Use **sequential-thinking**

### Agent Color Reference

Use these colored indicators for each agent in ALL output:

```
# Domain Specialists (Custom Agents)
🩵 api-integration-engineer (cyan) - API clients, OAuth, caching, rate limiting
🟢 data-pipeline-pro (green) - CSV/Excel, pandas, data validation
🟣 lead-enrichment-specialist (purple) - Name matching, owner discovery, pipeline
🔵 async-python-specialist (blue) - Async patterns, concurrency, throughput

# Core Agents
🟣 python-pro (purple) - General Python implementation
🟠 agent-organizer (orange) - Task decomposition, coordination
⚪ Explore (white) - Codebase exploration, finding files
⚪ Plan (white) - Architecture and design planning
⚪ general-purpose (white) - Complex research, multi-step tasks
🔷 Bash (blue) - Command execution, git operations
```

### Step 1: Announce Swarm Initiation

Output this EXACT format:

```
╔══════════════════════════════════════════════════════════════╗
║                     🐝 INITIATING SWARM                      ║
╚══════════════════════════════════════════════════════════════╝

Bringing in 🟠 agent-organizer to assign tasks for:
► "$ARGUMENTS"

⏳ Analyzing task complexity...
```

### Step 2: Call Agent Organizer

Use the Task tool to call the **agent-organizer** agent with this prompt:

"Analyze and decompose this task into subtasks that can be executed by specialized agents. Identify which agents to use, map dependencies, and determine which tasks can run in parallel.

Task: $ARGUMENTS

Project Context: This is a Python CLI tool for restaurant lead enrichment. Key components:
- main.py: Single-file CLI with async parallel processing
- Data Classes: Config, PersonInfo, RestaurantRecord
- CacheManager: File-based MD5-hashed cache in .cache/
- API Clients: GooglePlacesClient, PerplexityClient (via OpenRouter)
- Processing Pipeline: Name resolution → Owner discovery → Fuzzy matching
- Dependencies: aiohttp, pandas, openai, rapidfuzz, tenacity, tqdm

Available DOMAIN SPECIALIST agents (prefer these when applicable):
- api-integration-engineer: Building/fixing API integrations (Google Places, Perplexity, Whitepages), auth, caching, retry logic
- data-pipeline-pro: CSV/Excel handling, pandas operations, data validation, output formatting
- lead-enrichment-specialist: Name matching, owner discovery, fuzzy matching, enrichment pipeline logic
- async-python-specialist: Async patterns, aiohttp, semaphores, rate limiting, concurrency optimization

Available CORE agents:
- python-pro: General Python implementation (use when task doesn't fit a specialist)
- Explore: Codebase exploration, finding files, understanding patterns
- Plan: Architecture and design planning
- general-purpose: Complex research, web search, multi-step investigation
- Bash: Command execution, git operations, running tests

Agent Selection Priority:
1. PREFER domain specialists over python-pro when the task matches their expertise
2. Use api-integration-engineer for ANY API-related work
3. Use data-pipeline-pro for ANY CSV/pandas/data format work
4. Use lead-enrichment-specialist for matching/pipeline logic changes
5. Use async-python-specialist for concurrency/performance work
6. Fall back to python-pro only for general tasks that don't fit specialists

Available MCP tools (use when beneficial):
- serena: Symbolic code navigation (find_symbol, replace_symbol_body)
- morph-mcp: Smart file editing (edit_file) and search (warpgrep_codebase_search)
- playwright: Browser automation for testing web APIs
- chrome-devtools: API debugging and network inspection
- sequential-thinking: Complex multi-step reasoning

For each subtask, specify:
1. Agent: Which agent handles this (PREFER specialists)
2. Complexity: Low/Medium/High
3. Estimated tokens: Small (<2k), Medium (2-5k), Large (5k+)
4. MCP tools: List SPECIFIC MCP tools that SHOULD be used (be explicit):
   - serena: For code navigation/editing (specify: find_symbol, replace_symbol_body, etc.)
   - morph-mcp: For file editing (edit_file) or search (warpgrep_codebase_search)
   - sequential-thinking: For complex multi-step reasoning
   - 'none': Only if no MCP tools apply

Be specific about WHY each MCP tool helps the subtask.

Provide a clear execution plan with phases, identifying which agents can run in parallel."

### Step 3: Display Execution Plan

After agent-organizer responds, output the plan with colors and MCP indicators:

```
╔══════════════════════════════════════════════════════════════╗
║                   📋 SWARM EXECUTION PLAN                    ║
╚══════════════════════════════════════════════════════════════╝

📋 Task: [Brief summary]

┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: [Description]                          [PARALLEL]  │
├─────────────────────────────────────────────────────────────┤
│  ⚪ Explore                    │ [task]        │ ~1k tokens │
│  🩵 api-integration-engineer   │ [task]        │ ~4k tokens │
│     └─ 🔶 serena: find_symbol                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: [Description]                         [SEQUENTIAL] │
├─────────────────────────────────────────────────────────────┤
│  🟣 lead-enrichment-specialist │ [task]        │ ~3k tokens │
│     └─ 🟤 morph-mcp: edit_file                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      📊 ESTIMATES                           │
├─────────────────────────────────────────────────────────────┤
│  Agents: [X]  │  Phases: [Y]  │  Est. Tokens: ~[Z]k        │
│  MCPs Used: [N]  │  Parallel Efficiency: [X]%              │
└─────────────────────────────────────────────────────────────┘
```

**Parallel Efficiency** = (Total if sequential - Actual with parallel) / Total if sequential * 100
- Higher is better (more work done in parallel)

**If `--dry-run` was specified, STOP HERE and output:**
```
════════════════════════════════════════════════════════════════
DRY RUN COMPLETE - No agents were deployed
Estimated token usage: ~[X]k tokens
Run without --dry-run to execute this plan
════════════════════════════════════════════════════════════════
```

### Step 4: Deploy Agents

Output:
```
╔══════════════════════════════════════════════════════════════╗
║                    🚀 DEPLOYING AGENTS                       ║
╚══════════════════════════════════════════════════════════════╝
```

### Step 5: Execute Each Phase

For EACH phase, track time and show status with colors:

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: [Description]                                      │
│ Started: [timestamp]  │  Agents: [X]  │  Mode: PARALLEL     │
└─────────────────────────────────────────────────────────────┘

  ⚡ 🩵 api-integration-engineer starting...
     └─ Task: [brief description]
     └─ MCPs: 🔶 serena (code navigation)

  ⚡ ⚪ Explore starting...
     └─ Task: [brief description]
```

Then launch ALL agents for that phase in a SINGLE message with multiple Task tool calls.

**CRITICAL - MCP TOOL INJECTION**: For EACH agent's Task call, you MUST include MCP instructions in the prompt. Use this template:

```
[Agent's specific task description]

**MCP TOOLS - USE THESE:**
You have access to these MCP tools and SHOULD use them:

[If serena recommended]
- 🔶 **serena**: Use for precise code navigation and editing
  - `mcp__serena__find_symbol` to find functions/classes by name
  - `mcp__serena__get_symbols_overview` for file structure
  - `mcp__serena__replace_symbol_body` for precise edits
  - `mcp__serena__find_referencing_symbols` to find all usages

[If morph-mcp recommended]
- 🟤 **morph-mcp**: Use for fast file editing and search
  - `mcp__morph-mcp__edit_file` for efficient edits with minimal context
  - `mcp__morph-mcp__warpgrep_codebase_search` for intelligent code search

[If sequential-thinking recommended]
- 🟣 **sequential-thinking**: Use for complex reasoning
  - `mcp__sequential-thinking__sequentialthinking` for multi-step analysis

**IMPORTANT**: Actively use these MCP tools during your work. They are already available and will improve your output quality.
```

**TOKEN OPTIMIZATION**: If `--fast` flag was used, add `model: "haiku"` to Task calls for Low complexity subtasks.

**MCP SKIP**: If `--no-mcp` flag was used, do NOT include the MCP TOOLS section in agent prompts.

**CRITICAL**: Launch all phase agents in parallel (multiple Task calls in one message).

### Step 6: Report Agent Completions

As each agent completes, check its response for MCP tool usage and output with color and metrics:

```
  ✓ 🩵 api-integration-engineer completed
    ├─ Duration: [X]s
    ├─ Result: [1-2 sentence summary]
    ├─ Files: [count] modified
    └─ MCP: 🔶 serena (find_symbol, replace_symbol_body)
```

If an agent FAILS, output:
```
  ✗ 🩵 api-integration-engineer FAILED
    ├─ Duration: [X]s
    ├─ Error: [error description]
    └─ Recovery: [Attempting retry / Skipping / Blocking]
```

### Step 7: Handle Failures

If an agent fails:

1. **Non-critical agent**: Log the failure, continue with remaining agents
```
⚠️  Non-critical failure: ⚪ Explore
    Continuing with remaining agents...
```

2. **Critical agent (blocks other phases)**: Attempt ONE retry
```
🔄 Critical failure: 🩵 api-integration-engineer
   Attempting retry (1/1)...
```

3. **Retry also fails**: Stop the swarm
```
🛑 SWARM HALTED
   Critical agent 🩵 api-integration-engineer failed after retry

   Completed before failure:
   - [list of completed work]

   Manual intervention required for:
   - [remaining tasks]
```

### Step 8: Phase Transitions

Between phases, show metrics:
```
┌─────────────────────────────────────────────────────────────┐
│ ✓ PHASE 1 COMPLETE                                         │
├─────────────────────────────────────────────────────────────┤
│  Duration: [X]s  │  Agents: [Y]  │  Success: [Z]/[Y]       │
│  Files Changed: [N]  │  Lines Modified: ~[M]               │
└─────────────────────────────────────────────────────────────┘

Proceeding to Phase 2...
```

### Step 9: Final Summary

After all phases, show comprehensive metrics:
```
╔══════════════════════════════════════════════════════════════╗
║                    ✅ SWARM COMPLETE                         ║
╚══════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────┐
│                     📊 STATISTICS                           │
├─────────────────────────────────────────────────────────────┤
│  Total Duration     │  [X]s                                 │
│  Agents Deployed    │  [count]                              │
│  Phases Executed    │  [count]                              │
│  Success Rate       │  [X]%                                 │
├─────────────────────────────────────────────────────────────┤
│  Files Changed      │  [count]                              │
│  Lines Added        │  +[count]                             │
│  Lines Removed      │  -[count]                             │
├─────────────────────────────────────────────────────────────┤
│  MCP Tools Used     │  [count]                              │
│  Code Navigations   │  [count] (serena)                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   🤖 AGENTS DEPLOYED                        │
├─────────────────────────────────────────────────────────────┤
│  🩵 api-integration-engineer  │ ✓ 15s │ Built client │🔶 serena│
│  🟣 lead-enrichment-specialist│ ✓ 12s │ Updated pipe │🟤 morph │
│  ⚪ Explore                   │ ✓  8s │ Found patterns│ -      │
│  🔷 Bash                      │ ✓  5s │ Ran tests    │ -       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     📋 SUMMARY                              │
├─────────────────────────────────────────────────────────────┤
│  ✓ [Key outcome 1]                                         │
│  ✓ [Key outcome 2]                                         │
│  ✓ [Key outcome 3]                                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   📁 FILES CHANGED                          │
├─────────────────────────────────────────────────────────────┤
│  • main.py                              [+125 lines]       │
│  • requirements.txt                     [+3 lines]         │
└─────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════
                    All tasks completed successfully.
════════════════════════════════════════════════════════════════
```

## Agent Reference with Colors

### Domain Specialists (Custom - PREFER THESE)
| Color | Agent | Domain | Token Usage | Best For |
|-------|-------|--------|-------------|----------|
| 🩵 | **api-integration-engineer** | API clients | Medium-Large | Google/Perplexity/Whitepages APIs, caching, retry |
| 🟢 | **data-pipeline-pro** | Data processing | Medium | CSV/Excel, pandas, validation, output format |
| 🟣 | **lead-enrichment-specialist** | Business logic | Medium | Name matching, owner discovery, pipeline flow |
| 🔵 | **async-python-specialist** | Concurrency | Medium | Async patterns, rate limiting, throughput |

### Core Agents
| Color | Agent | Domain | Token Usage |
|-------|-------|--------|-------------|
| 🟣 | **python-pro** | Python general | Medium-Large |
| ⚪ | **Explore** | Codebase exploration | Small |
| ⚪ | **Plan** | Architecture and design | Medium |
| ⚪ | **general-purpose** | Complex research | Large |
| 🔷 | **Bash** | Command execution | Small |
| 🟠 | **agent-organizer** | Task decomposition | Medium |

### Agent Selection Guide

| Task Type | Primary Agent | Why |
|-----------|---------------|-----|
| New API client | 🩵 api-integration-engineer | Knows aiohttp patterns, caching |
| API debugging | 🩵 api-integration-engineer | Understands retry logic, errors |
| CSV/Excel handling | 🟢 data-pipeline-pro | pandas expertise |
| Data validation | 🟢 data-pipeline-pro | Knows data cleaning patterns |
| Name matching | 🟣 lead-enrichment-specialist | Fuzzy matching expertise |
| Pipeline changes | 🟣 lead-enrichment-specialist | Understands enrichment flow |
| Async optimization | 🔵 async-python-specialist | Semaphore, concurrency |
| Rate limiting | 🔵 async-python-specialist | Throughput optimization |
| Find patterns | ⚪ Explore | Codebase navigation |
| Research APIs | ⚪ general-purpose | Web search, docs |
| Run tests | 🔷 Bash | Command execution |

## Token Usage Guide

**Estimated tokens per agent complexity:**
- **Small** (<2k): Simple lookups, small edits, config changes
- **Medium** (2-5k): Feature implementation, API integration
- **Large** (5k+): Complex features, multi-file changes, research

**Tips to reduce token usage:**
1. Use `--fast` flag to use haiku model for simple subtasks
2. Be specific in task description to reduce exploration
3. Use `--focus=N` to run only needed phases
4. Use `--dry-run` first to preview and refine the plan

## Examples

### Standard Execution
```
/swarm Add Whitepages API integration for owner lookup
```

### Dry Run (Preview Only)
```
/swarm --dry-run Refactor caching system to use Redis
```

### Fast Mode (Reduced Tokens)
```
/swarm --fast Add a simple health check endpoint
```

### Focus on Specific Phase
```
/swarm --focus=2 Add batch processing with rate limiting
```

## Example Output

```
╔══════════════════════════════════════════════════════════════╗
║                     🐝 INITIATING SWARM                      ║
╚══════════════════════════════════════════════════════════════╝

Bringing in 🟠 agent-organizer to assign tasks for:
► "Add Whitepages API integration for owner lookup"

⏳ Analyzing task complexity...

╔══════════════════════════════════════════════════════════════╗
║                   📋 SWARM EXECUTION PLAN                    ║
╚══════════════════════════════════════════════════════════════╝

📋 Task: Implement Whitepages API client for owner enrichment

┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: Research & Design                      [PARALLEL]  │
├─────────────────────────────────────────────────────────────┤
│  ⚪ Explore                   │ Find API patterns │ ~1k tkns│
│  ⚪ general-purpose           │ Research WP API   │ ~2k tkns│
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: Implementation                         [PARALLEL]  │
├─────────────────────────────────────────────────────────────┤
│  🩵 api-integration-engineer  │ Build API client  │ ~4k tkns│
│     └─ 🔶 serena: find_symbol, replace_symbol_body          │
│  🟣 lead-enrichment-specialist│ Update pipeline   │ ~3k tkns│
│     └─ 🟤 morph-mcp: edit_file                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: Testing                               [SEQUENTIAL] │
├─────────────────────────────────────────────────────────────┤
│  🔵 async-python-specialist   │ Add rate limiting │ ~2k tkns│
│  🔷 Bash                      │ Run tests         │ ~1k tkns│
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      📊 ESTIMATES                           │
├─────────────────────────────────────────────────────────────┤
│  Agents: 6   │  Phases: 3   │  Est. Tokens: ~13k           │
│  Parallel Efficiency: 54%  │  Est. Time: ~40s              │
└─────────────────────────────────────────────────────────────┘
```

Now begin the swarm execution for the provided task.
