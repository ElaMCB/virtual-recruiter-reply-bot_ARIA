# Interview Agent - Quick Start Guide

Get ARIA's interview agent running in 5 minutes.

## Installation

### Step 1: Install Playwright

```bash
pip install playwright
playwright install chromium
```

### Step 2: Verify Integration

The interview agent is already in `agents/interview_agent.py`. Just import it!

## Quick Test

### Test Interview Agent Standalone

```python
from agents.interview_agent import InterviewAgent

# Create agent (will use default LLM if not configured)
agent = InterviewAgent()

# Test browser
agent.start_interview("https://example.com")
status = agent.get_interview_status()
print(status)
agent.close_interview()
```

### Test with ARIA

```python
# In ARIA's main.py or orchestrator
from agents.interview_agent import InterviewAgent
from core.llm_processor import LLMProcessor
from core.state_manager import StateManager

# Initialize
llm = LLMProcessor()
state = StateManager()
interview_agent = InterviewAgent(
    llm_processor=llm,
    state_manager=state
)

# Start interview from email link
result = interview_agent.start_interview(
    interview_url="https://interview-platform.com/abc123",
    company="TechCorp",
    position="Software Engineer"
)
```

## Common Tasks

### Analyze Code Snippet

```python
result = interview_agent.analyze_code_snippet()
print(result["formatted_report"])
```

### Answer Question

```python
result = interview_agent.answer_question()
print(f"Q: {result['question']}")
print(f"A: {result['answer']}")
```

### Navigate Interview

```python
# Click a button
interview_agent.interact_with_page("click", target="Start Interview")

# Fill a form
interview_agent.interact_with_page("fill", target="name", value="John Doe")
```

## Integration with Email Agent

The interview agent automatically triggers when email agent detects interview links. See orchestrator updates for full integration.

## Next Steps

1. Read full documentation: `docs/INTERVIEW_AGENT.md`
2. Update orchestrator to detect interview links
3. Test with sample interview link

---

**Ready!** The interview agent is now part of your ARIA workflow.

