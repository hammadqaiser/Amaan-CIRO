---
name: ciro-agent-generator
description: Generate boilerplate and standard components for an Amaan CIRO Agent. Use this when starting the development of a new agent out of the 8 required agents, to ensure it implements the standard BaseAgent contract, proper Antigravity trace logging, FastAPI endpoints, Pydantic models, and error handling.
---

# CIRO Agent Generator

Use this skill to quickly bootstrap or validate one of the 8 Amaan CIRO agents.

## Core Requirements Every Agent Must Have:
1. Inherits from `BaseAgent`.
2. Input and Output Pydantic models (`<AgentName>Input`, `<AgentName>Output`).
3. An `__init__` that calls `super().__init__("AgentName")`.
4. A primary `async def process(self, input: <AgentName>Input) -> <AgentName>Output` method.
5. All external API calls MUST be wrapped in `try/except` blocks with a defined fallback strategy.
6. A `self.log_trace()` call returning a trace dict to be included in the output.

## Code Generation Structure:
When asked to scaffold an agent, output the following structure:

```python
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
import uuid
# Import BaseAgent (Assume it's available in backend.agents.base_agent)
from backend.agents.base_agent import BaseAgent

# 1. Pydantic Models
class MyAgentInput(BaseModel):
    # Add input fields here based on AGENTS.md
    pass

class MyAgentOutput(BaseModel):
    # Add output fields here based on AGENTS.md
    trace: dict

# 2. Agent Class
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("MyAgent")
        
    async def process(self, input_data: MyAgentInput) -> MyAgentOutput:
        trace_id = str(uuid.uuid4())
        reasoning_steps = []
        fallback_triggered = False
        
        # 3. Logic & Fallbacks
        try:
            # Main logic here
            reasoning_steps.append("Started processing...")
            # ...
        except Exception as e:
            fallback_triggered = True
            reasoning_steps.append(f"Error encountered: {str(e)}. Using fallback.")
            
        # 4. Trace Logging
        trace = self.log_trace(
            trace_id=trace_id,
            input_data=input_data.model_dump(),
            reasoning_steps=reasoning_steps,
            confidence_score=0.85, # dynamic in reality
            decision_made={"status": "completed"},
            alternative_considered=None,
            fallback_triggered=fallback_triggered
        )
        
        return MyAgentOutput(
            # fields...
            trace=trace
        )
```

## Review Checklist:
When reviewing an agent's code, verify:
- [ ] No unhandled exceptions can bubble up from `process`.
- [ ] `self.log_trace()` is called with all required arguments.
- [ ] Fallback paths never crash the pipeline.
- [ ] Gemini API calls use `self.call_gemini()`.
