# ARIA Interview Agent

ARIA's interview agent handles automated interactions with HR interview systems, completing the recruiter interaction workflow from initial contact through the interview process.

## Overview

The Interview Agent extends ARIA's capabilities to handle:
- **Automated Interview Navigation** - Opens interview links and navigates interview platforms
- **Code Analysis** - Reviews code snippets and provides intelligent feedback
- **Question Answering** - Generates professional responses to interview questions
- **Interview Progress Tracking** - Monitors and logs interview interactions

## How It Fits into ARIA

```
Email Agent → Initial Contact
    ↓
SMS Agent → Screening Questions
    ↓
Interview Agent → Technical Interview ← YOU ARE HERE
    ↓
Follow-up Agent → Post-Interview
```

## Features

### Browser Automation
- Opens interview URLs from recruiter emails
- Navigates interview platforms automatically
- Handles dynamic content and modern web interfaces
- Screenshot capture for debugging

### Code Analysis
- Extracts code snippets from interview pages
- Analyzes code for bugs, security issues, and best practices
- Provides quality scores and improvement suggestions
- Supports multiple programming languages

### Intelligent Question Answering
- Extracts questions from interview interfaces
- Generates context-aware responses using ARIA's LLM
- Maintains conversation context across interview turns
- Tailors answers to question type (technical, behavioral, coding)

### State Management
- Integrates with ARIA's state manager
- Tracks interview progress and history
- Saves conversation context for follow-ups
- Links interview sessions to job applications

## Installation

### Prerequisites

1. **Install Playwright**:
```bash
pip install playwright
playwright install chromium
```

2. **Requirements are already updated** in `requirements.txt`

### Integration

The interview agent is automatically available when you:
1. Import it in ARIA's orchestrator
2. Pass LLM processor and state manager instances
3. Configure in ARIA's main configuration

## Usage

### Basic Usage

```python
from agents.interview_agent import InterviewAgent
from core.llm_processor import LLMProcessor
from core.state_manager import StateManager

# Initialize with ARIA's components
llm = LLMProcessor()
state = StateManager()
agent = InterviewAgent(llm_processor=llm, state_manager=state)

# Start an interview
result = agent.start_interview(
    interview_url="https://interview-platform.com/interview/abc123",
    company="TechCorp",
    position="Senior Software Engineer"
)

# Analyze code snippet
code_analysis = agent.analyze_code_snippet()

# Answer a question
answer_result = agent.answer_question()
```

## Important Disclaimer

**This tool is for educational and research purposes only.**

- Using automation to complete interviews may violate terms of service
- Many systems detect automation and may flag your account
- This should **NOT** be used to misrepresent yourself in real job interviews
- Use responsibly and ethically

## Safety Features

### Human Oversight
- Optional approval for all answers
- Screenshot capture for review
- Manual mode available
- Escalation to human for important decisions

### Detection Mitigation
- Human-like delays between actions
- Natural interaction patterns
- Configurable behavior
- Transparent logging

### Compliance
- All interactions logged
- Full conversation history
- Reviewable decision trail
- Respects platform terms (when used ethically)

## Troubleshooting

### Browser Won't Start
```bash
# Reinstall Playwright
pip uninstall playwright
pip install playwright
playwright install chromium
```

### Code Not Detected
- Check page content extraction
- Verify code block formats
- Enable screenshot debugging
- Review page source

### Element Not Found
- Increase wait times
- Check element selectors
- Verify page loaded completely
- Use manual element selection

## Related Documentation

- `INTERVIEW_QUICK_START.md` - Quick setup guide
- `ARCHITECTURE.md` - System design
- `gmail_setup.md` - Email integration
- `ollama_setup.md` - LLM setup

---

**Remember**: Use responsibly and ethically. This is a tool to assist, not to replace your genuine interview performance.

