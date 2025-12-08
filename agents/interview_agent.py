"""Interview agent for ARIA - handles automated interview interactions."""

import time
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed. Browser automation will not work.")


class InterviewAgent:
    """Agent for automating interactions with HR interview systems."""
    
    def __init__(self, llm_processor=None, state_manager=None, headless: bool = False):
        """
        Initialize interview agent.
        
        Args:
            llm_processor: ARIA's LLM processor instance
            state_manager: ARIA's state manager for conversation tracking
            headless: Whether to run browser in headless mode
        """
        self.llm_processor = llm_processor
        self.state_manager = state_manager
        self.headless = headless
        
        # Browser automation
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_active = False
        
        # Interview state
        self.interview_state = {
            "current_step": None,
            "interview_url": None,
            "company": None,
            "position": None,
            "questions_answered": [],
            "code_snippets_analyzed": [],
            "started_at": None,
        }
    
    def start_interview(self, interview_url: str, company: str = None, position: str = None) -> Dict[str, Any]:
        """
        Start interview session by navigating to URL.
        
        Args:
            interview_url: URL of the interview system
            company: Company name (optional)
            position: Position title (optional)
        
        Returns:
            Status and initial page content
        """
        try:
            # Start browser
            if not self._start_browser():
                return {"success": False, "error": "Failed to start browser"}
            
            # Navigate to interview URL
            if not self._navigate_to(interview_url):
                return {"success": False, "error": "Failed to navigate to interview URL"}
            
            # Get initial page content
            page_content = self._get_page_content()
            
            # Update state
            self.interview_state.update({
                "current_step": "started",
                "interview_url": interview_url,
                "company": company,
                "position": position,
                "started_at": datetime.now().isoformat(),
            })
            
            # Save to state manager if available
            if self.state_manager:
                self.state_manager.save_interview_state(
                    interview_url=interview_url,
                    state=self.interview_state
                )
            
            # Analyze page to understand what to do next
            next_action = self._analyze_page_and_plan(page_content)
            
            return {
                "success": True,
                "page_content": page_content,
                "next_action": next_action,
                "message": "Interview session started"
            }
        except Exception as e:
            logger.error(f"Error starting interview: {e}")
            return {"success": False, "error": str(e)}
    
    def analyze_code_snippet(self, code: Optional[str] = None, language: str = "python") -> Dict[str, Any]:
        """
        Analyze a code snippet from the interview.
        
        Args:
            code: Code snippet (if None, will try to extract from page)
            language: Programming language
        
        Returns:
            Analysis results
        """
        # If code not provided, try to extract from page
        if not code:
            page_content = self._get_page_content()
            code = self._extract_code_from_page(page_content)
        
        if not code:
            return {"success": False, "error": "No code snippet found"}
        
        # Analyze code
        analysis = self._analyze_code(code, language)
        
        # Generate response for interview using LLM
        response_text = self._generate_code_analysis_response(analysis)
        
        self.interview_state["code_snippets_analyzed"].append({
            "code_preview": code[:200] + "..." if len(code) > 200 else code,
            "analysis": analysis,
            "response": response_text,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Update state manager
        if self.state_manager:
            self.state_manager.update_interview_state(
                interview_url=self.interview_state["interview_url"],
                update={"code_snippets_analyzed": self.interview_state["code_snippets_analyzed"]}
            )
        
        return {
            "success": True,
            "analysis": analysis,
            "response": response_text,
            "formatted_report": self._format_analysis_report(analysis)
        }
    
    def answer_question(self, question: Optional[str] = None) -> Dict[str, Any]:
        """
        Answer a question from the interview.
        
        Args:
            question: Question text (if None, will try to extract from page)
        
        Returns:
            Answer and response
        """
        # Extract question from page if not provided
        if not question:
            page_content = self._get_page_content()
            question = self._extract_question_from_page(page_content)
        
        if not question:
            return {"success": False, "error": "No question found on page"}
        
        # Generate answer using ARIA's LLM processor
        if self.llm_processor:
            try:
                # Use ARIA's prompt system
                prompt = self._build_interview_answer_prompt(question)
                response_data = self.llm_processor.generate_response(
                    message=prompt,
                    channel='interview',
                    conversation_state={},
                    context={'question': question}
                )
                answer = response_data.get('response', '') if isinstance(response_data, dict) else str(response_data)
            except Exception as e:
                logger.error(f"LLM answer generation failed: {e}")
                answer = "I would approach this by analyzing the requirements and implementing a solution that follows best practices."
        else:
            answer = "Based on my experience, I would approach this systematically, considering best practices and edge cases."
        
        self.interview_state["questions_answered"].append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Update state manager
        if self.state_manager:
            self.state_manager.update_interview_state(
                interview_url=self.interview_state["interview_url"],
                update={"questions_answered": self.interview_state["questions_answered"]}
            )
        
        return {
            "success": True,
            "question": question,
            "answer": answer
        }
    
    def interact_with_page(self, action: str, target: Optional[str] = None, value: Optional[str] = None) -> Dict[str, Any]:
        """
        Interact with the page (click, fill, etc.).
        
        Args:
            action: Action to take (click, fill, wait)
            target: Target element (button text, field name, etc.)
            value: Value to fill (if action is fill)
        
        Returns:
            Result of interaction
        """
        try:
            if action == "click":
                if not target:
                    return {"success": False, "error": "Target required for click action"}
                
                selector = self._find_element_by_text(target)
                if selector:
                    success = self._click_element(selector)
                    if success:
                        time.sleep(2)  # Wait for page update
                        page_content = self._get_page_content()
                        return {
                            "success": True,
                            "action": f"Clicked {target}",
                            "page_content": page_content
                        }
                
                return {"success": False, "error": f"Could not find element: {target}"}
            
            elif action == "fill":
                if not target or not value:
                    return {"success": False, "error": "Target and value required for fill action"}
                
                page_content = self._get_page_content()
                inputs = page_content.get("inputs", [])
                
                for inp in inputs:
                    if target.lower() in inp.get("name", "").lower() or target.lower() in inp.get("placeholder", "").lower():
                        selector = f"input[name='{inp['name']}']" if inp.get("name") else f"input[placeholder='{inp['placeholder']}']"
                        success = self._fill_input(selector, value)
                        if success:
                            return {"success": True, "action": f"Filled {target} with value"}
                
                return {"success": False, "error": f"Could not find input field: {target}"}
            
            elif action == "wait":
                if target:
                    success = self._wait_for_text(target, timeout=10000)
                    return {"success": success, "action": f"Waited for {target}"}
                else:
                    time.sleep(2)
                    return {"success": True, "action": "Waited 2 seconds"}
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"Error interacting with page: {e}")
            return {"success": False, "error": str(e)}
    
    def get_interview_status(self) -> Dict[str, Any]:
        """Get current interview status."""
        page_content = self._get_page_content() if self.is_active else {}
        
        return {
            "active": self.is_active,
            "current_step": self.interview_state["current_step"],
            "company": self.interview_state.get("company"),
            "position": self.interview_state.get("position"),
            "questions_answered": len(self.interview_state["questions_answered"]),
            "code_snippets_analyzed": len(self.interview_state["code_snippets_analyzed"]),
            "page_url": page_content.get("url", "N/A"),
            "started_at": self.interview_state.get("started_at"),
        }
    
    def close_interview(self):
        """Close interview session."""
        self._close_browser()
        self.interview_state = {
            "current_step": None,
            "interview_url": None,
            "company": None,
            "position": None,
            "questions_answered": [],
            "code_snippets_analyzed": [],
            "started_at": None,
        }
    
    # Browser automation methods
    def _start_browser(self) -> bool:
        """Start browser session."""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available. Install with: pip install playwright && playwright install")
            return False
        
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.context = self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            self.page = self.context.new_page()
            self.is_active = True
            logger.info("Browser started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False
    
    def _navigate_to(self, url: str) -> bool:
        """Navigate to a URL."""
        if not self.is_active or not self.page:
            logger.error("Browser not started")
            return False
        
        try:
            self.page.goto(url, wait_until="networkidle", timeout=30000)
            logger.info(f"Navigated to {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def _get_page_content(self) -> Dict[str, Any]:
        """Extract text content and structure from current page."""
        if not self.is_active or not self.page:
            return {"error": "Browser not started"}
        
        try:
            text_content = self.page.inner_text("body")
            
            elements = self.page.query_selector_all("p, h1, h2, h3, h4, h5, h6, div, span, button, input, textarea")
            element_texts = []
            for elem in elements[:100]:
                try:
                    text = elem.inner_text()
                    tag = elem.evaluate("el => el.tagName.toLowerCase()")
                    if text.strip():
                        element_texts.append({"tag": tag, "text": text.strip()})
                except:
                    continue
            
            inputs = []
            for input_elem in self.page.query_selector_all("input, textarea, select"):
                try:
                    input_type = input_elem.get_attribute("type") or "text"
                    placeholder = input_elem.get_attribute("placeholder") or ""
                    name = input_elem.get_attribute("name") or ""
                    value = input_elem.input_value() if input_type != "file" else ""
                    inputs.append({
                        "type": input_type,
                        "name": name,
                        "placeholder": placeholder,
                        "value": value
                    })
                except:
                    continue
            
            buttons = []
            for button in self.page.query_selector_all("button, input[type='submit'], a[role='button']"):
                try:
                    text = button.inner_text() or button.get_attribute("aria-label") or ""
                    buttons.append(text.strip())
                except:
                    continue
            
            return {
                "text_content": text_content,
                "elements": element_texts,
                "inputs": inputs,
                "buttons": buttons,
                "url": self.page.url
            }
        except Exception as e:
            logger.error(f"Failed to get page content: {e}")
            return {"error": str(e)}
    
    def _find_element_by_text(self, text: str, partial: bool = True) -> Optional[str]:
        """Find element containing text and return selector."""
        if not self.is_active or not self.page:
            return None
        
        try:
            if partial:
                selector = f"text={text}"
            else:
                selector = f"text='{text}'"
            
            element = self.page.query_selector(selector)
            if element:
                try:
                    id_attr = element.get_attribute("id")
                    if id_attr:
                        return f"#{id_attr}"
                    class_attr = element.get_attribute("class")
                    if class_attr:
                        return f".{class_attr.split()[0]}"
                    return selector
                except:
                    return selector
            return None
        except Exception as e:
            logger.error(f"Failed to find element: {e}")
            return None
    
    def _click_element(self, selector: str) -> bool:
        """Click an element by selector."""
        if not self.is_active or not self.page:
            return False
        
        try:
            self.page.click(selector, timeout=5000)
            time.sleep(1)
            logger.info(f"Clicked element: {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {e}")
            return False
    
    def _fill_input(self, selector: str, text: str) -> bool:
        """Fill an input field."""
        if not self.is_active or not self.page:
            return False
        
        try:
            self.page.fill(selector, text)
            logger.info(f"Filled input {selector} with text")
            return True
        except Exception as e:
            logger.error(f"Failed to fill input {selector}: {e}")
            return False
    
    def _wait_for_text(self, text: str, timeout: int = 10000) -> bool:
        """Wait for text to appear on page."""
        if not self.is_active or not self.page:
            return False
        
        try:
            self.page.wait_for_selector(f"text={text}", timeout=timeout)
            return True
        except:
            return False
    
    def _close_browser(self):
        """Close browser session."""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.is_active = False
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    # Analysis methods
    def _analyze_page_and_plan(self, page_content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze page content and determine next action."""
        text = page_content.get("text_content", "").lower()
        buttons = page_content.get("buttons", [])
        
        if any(word in text for word in ["code", "snippet", "function", "class"]):
            return {"action": "analyze_code", "reasoning": "Code snippet detected on page"}
        elif any(word in text for word in ["question", "answer", "what", "how", "why"]):
            return {"action": "answer_question", "reasoning": "Question detected on page"}
        elif "start" in text or any("start" in b.lower() for b in buttons):
            return {"action": "click", "target": "start", "reasoning": "Start button found"}
        elif "next" in text or any("next" in b.lower() for b in buttons):
            return {"action": "click", "target": "next", "reasoning": "Next button found"}
        else:
            return {"action": "analyze", "reasoning": "Analyzing page structure"}
    
    def _extract_code_from_page(self, page_content: Dict[str, Any]) -> Optional[str]:
        """Extract code snippet from page content."""
        text = page_content.get("text_content", "")
        elements = page_content.get("elements", [])
        
        code_patterns = [
            r'```[\s\S]*?```',
            r'<code>[\s\S]*?</code>',
            r'<pre>[\s\S]*?</pre>'
        ]
        
        for pattern in code_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                code = matches[0]
                code = re.sub(r'```\w*', '', code)
                code = re.sub(r'```', '', code)
                code = re.sub(r'<code>', '', code, flags=re.IGNORECASE)
                code = re.sub(r'</code>', '', code, flags=re.IGNORECASE)
                code = re.sub(r'<pre>', '', code, flags=re.IGNORECASE)
                code = re.sub(r'</pre>', '', code, flags=re.IGNORECASE)
                return code.strip()
        
        for elem in elements:
            if elem.get("tag") in ["code", "pre"]:
                code_text = elem.get("text", "")
                if len(code_text) > 20 and any(keyword in code_text for keyword in ["def ", "function", "class ", "import ", "="]):
                    return code_text
        
        return None
    
    def _extract_question_from_page(self, page_content: Dict[str, Any]) -> Optional[str]:
        """Extract question text from page."""
        text = page_content.get("text_content", "")
        elements = page_content.get("elements", [])
        
        question_keywords = ["question", "what", "how", "why", "explain", "describe", "?"]
        
        for elem in elements:
            elem_text = elem.get("text", "")
            if any(keyword in elem_text.lower() for keyword in question_keywords):
                if "?" in elem_text or len(elem_text) > 20:
                    return elem_text
        
        sentences = text.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in question_keywords):
                if "?" in sentence:
                    return sentence.strip()
        
        return None
    
    def _analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Analyze code for issues (simplified version)."""
        issues = []
        
        # Basic syntax checking for Python
        if language.lower() == "python":
            try:
                import ast
                ast.parse(code)
            except SyntaxError as e:
                issues.append({
                    "type": "syntax_error",
                    "severity": "high",
                    "message": f"Syntax error: {e.msg} at line {e.lineno}",
                    "line": e.lineno
                })
        
        # Basic code smell detection
        lines = code.split('\n')
        if len(lines) > 50:
            issues.append({
                "type": "code_smell",
                "severity": "medium",
                "message": "Function/block is very long (>50 lines). Consider breaking it into smaller functions."
            })
        
        quality_score = max(0, 100 - (len(issues) * 10))
        
        return {
            "issues": issues,
            "quality_score": quality_score,
            "language": language,
            "code_length": len(code)
        }
    
    def _generate_code_analysis_response(self, analysis: Dict[str, Any]) -> str:
        """Generate human-like response about code analysis."""
        issues = analysis.get("issues", [])
        quality_score = analysis.get("quality_score", 100)
        
        if not issues:
            return "This code looks good! I don't see any obvious issues. The implementation appears clean and follows good practices."
        
        high_severity = [i for i in issues if i.get("severity") == "high"]
        medium_severity = [i for i in issues if i.get("severity") == "medium"]
        
        response_parts = []
        
        if high_severity:
            response_parts.append(f"I found {len(high_severity)} critical issue(s):")
            for issue in high_severity[:3]:
                response_parts.append(f"- {issue.get('message', 'Issue found')}")
        
        if medium_severity:
            response_parts.append(f"\nThere are also {len(medium_severity)} issue(s) to consider:")
            for issue in medium_severity[:2]:
                response_parts.append(f"- {issue.get('message', 'Issue found')}")
        
        response_parts.append(f"\nOverall quality score: {quality_score}/100")
        
        return "\n".join(response_parts)
    
    def _format_analysis_report(self, analysis: Dict[str, Any]) -> str:
        """Format analysis results as a readable report."""
        report = f"Code Analysis Report\n"
        report += f"{'='*50}\n"
        report += f"Language: {analysis.get('language', 'unknown')}\n"
        report += f"Quality Score: {analysis.get('quality_score', 0)}/100\n\n"
        
        issues = analysis.get('issues', [])
        if issues:
            report += f"Issues Found ({len(issues)}):\n"
            for i, issue in enumerate(issues, 1):
                severity = issue.get('severity', 'unknown').upper()
                message = issue.get('message', 'No description')
                report += f"{i}. [{severity}] {message}\n"
        else:
            report += "No issues found!\n"
        
        return report
    
    def _build_interview_answer_prompt(self, question: str) -> str:
        """Build prompt for answering interview questions."""
        return f"""You are in a technical interview. Answer the following question professionally and concisely:

Question: {question}

Provide a clear, technical answer that demonstrates your knowledge. Keep it to 2-3 sentences unless the question requires more detail."""

