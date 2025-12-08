# Interview Agent Integration Guide

This guide shows how the interview agent has been integrated into ARIA.

## What Was Added

### Files Added
- ✅ `agents/interview_agent.py` - Interview agent implementation
- ✅ `docs/INTERVIEW_AGENT.md` - Full documentation
- ✅ `docs/INTERVIEW_QUICK_START.md` - Quick setup guide

### Files Updated
- ✅ `requirements.txt` - Added playwright>=1.40.0
- ✅ `core/orchestrator.py` - Added interview link detection and handling
- ✅ `core/state_manager.py` - Added interview state management methods

## Integration Details

### Orchestrator Integration

The orchestrator now:
1. Detects interview links in email bodies
2. Automatically starts interview sessions
3. Links interview sessions to conversation threads
4. Updates conversation stage to 'scheduling'

### State Manager Integration

Added methods:
- `save_interview_state()` - Save interview session state
- `get_interview_state()` - Retrieve interview session state
- `update_interview_state()` - Update interview session state

New database table: `interview_sessions`

## Usage

### Automatic Detection

When ARIA processes an email with an interview link, it automatically:
1. Detects the link
2. Starts the interview session
3. Saves state to database
4. Updates conversation stage

### Manual Usage

```python
from agents.interview_agent import InterviewAgent
from core.llm_processor import LLMProcessor
from core.state_manager import StateManager

llm = LLMProcessor()
state = StateManager()
agent = InterviewAgent(llm_processor=llm, state_manager=state)

result = agent.start_interview(
    interview_url="https://interview-platform.com/abc123",
    company="TechCorp",
    position="Software Engineer"
)
```

## Installation

1. Install Playwright:
```bash
pip install playwright
playwright install chromium
```

2. Requirements already updated in `requirements.txt`

3. Ready to use! The orchestrator will automatically detect interview links.

## Configuration

Add to `.env` (optional):
```bash
INTERVIEW_HEADLESS=false  # Set to true for headless browser
```

## Next Steps

1. Test with a sample interview link
2. Review interview sessions in database
3. Customize interview agent behavior as needed

---

**Integration complete!** The interview agent is now part of ARIA's workflow.

