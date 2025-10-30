"""
La Secretaria - Email Intelligence Agent

Specializes in email triage, intelligent routing, and extracting actionable
information from email communications.
"""

from typing import Any, Dict
from datetime import datetime
import re

from .base_agent import BaseAgent, AgentCapability


class LaSecretaria(BaseAgent):
    """
    Email Intelligence Agent

    La Secretaria processes incoming emails, extracts key information,
    identifies action items, and routes messages to appropriate handlers.
    """

    def __init__(self):
        """Initialize La Secretaria with email processing capabilities."""
        super().__init__("La Secretaria")

        # Set agent capabilities
        self.set_capability(AgentCapability.EMAIL_PROCESSING, True)
        self.set_capability(AgentCapability.PRIORITY_ASSESSMENT, True)
        self.set_capability(AgentCapability.METADATA_EXTRACTION, True)

        # Email patterns for detection
        self.urgent_keywords = [
            "urgent", "asap", "immediate", "emergency",
            "critical", "time-sensitive", "deadline"
        ]

        self.action_patterns = [
            r"please\s+(\w+)",
            r"need\s+to\s+(\w+)",
            r"must\s+(\w+)",
            r"should\s+(\w+)"
        ]

        # Training data
        self.sender_priority_map = {}
        self.subject_patterns = {}

    async def process(self, event) -> Dict[str, Any]:
        """
        Process email-related events.

        Args:
            event: SystemEvent containing email data

        Returns:
            Dictionary with email analysis and recommendations
        """
        if event.type != "email_received":
            return {
                "agent": self.agent_name,
                "status": "skipped",
                "reason": f"Event type '{event.type}' not handled by this agent"
            }

        email_data = event.payload

        # Extract email components
        sender = email_data.get("from", "unknown")
        subject = email_data.get("subject", "")
        body = email_data.get("body", "")
        recipients = email_data.get("to", [])

        # Analyze the email
        analysis = {
            "agent": self.agent_name,
            "status": "processed",
            "timestamp": datetime.now().isoformat(),
            "email_id": email_data.get("id", "unknown"),
            "sender": sender,
            "subject": subject,
            "priority": self._assess_priority(sender, subject, body),
            "urgency": self._detect_urgency(subject, body),
            "action_items": self._extract_action_items(body),
            "categories": self._categorize_email(subject, body),
            "requires_response": self._requires_response(body),
            "suggested_actions": []
        }

        # Generate suggested actions
        analysis["suggested_actions"] = self._generate_suggestions(analysis)

        return analysis

    def _assess_priority(self, sender: str, subject: str, body: str) -> str:
        """
        Assess email priority based on sender, subject, and content.

        Args:
            sender: Email sender
            subject: Email subject
            body: Email body

        Returns:
            Priority level: 'high', 'medium', or 'low'
        """
        # Check sender priority map from training
        sender_priority = self.sender_priority_map.get(sender, "medium")

        # Check for urgent keywords
        text = f"{subject} {body}".lower()
        urgent_count = sum(1 for keyword in self.urgent_keywords if keyword in text)

        if urgent_count >= 2 or sender_priority == "high":
            return "high"
        elif urgent_count == 1:
            return "medium"
        else:
            return "low"

    def _detect_urgency(self, subject: str, body: str) -> Dict[str, Any]:
        """
        Detect urgency indicators in the email.

        Args:
            subject: Email subject
            body: Email body

        Returns:
            Dictionary with urgency analysis
        """
        text = f"{subject} {body}".lower()

        urgency_indicators = []
        for keyword in self.urgent_keywords:
            if keyword in text:
                urgency_indicators.append(keyword)

        # Check for deadline mentions
        deadline_pattern = r"(by|before|due)\s+(\w+\s+\d+|\d+/\d+)"
        deadlines = re.findall(deadline_pattern, text, re.IGNORECASE)

        return {
            "is_urgent": len(urgency_indicators) > 0,
            "urgency_indicators": urgency_indicators,
            "deadlines_mentioned": len(deadlines),
            "deadline_phrases": [" ".join(d) for d in deadlines]
        }

    def _extract_action_items(self, body: str) -> list:
        """
        Extract action items from email body.

        Args:
            body: Email body text

        Returns:
            List of identified action items
        """
        action_items = []

        for pattern in self.action_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            action_items.extend(matches)

        # Look for numbered or bulleted lists
        list_pattern = r"(?:^|\n)\s*[\d\-\*]\.\s*(.+?)(?=\n|$)"
        list_items = re.findall(list_pattern, body, re.MULTILINE)
        action_items.extend(list_items)

        # Remove duplicates and clean
        action_items = list(set([item.strip() for item in action_items if item.strip()]))

        return action_items[:10]  # Limit to top 10 items

    def _categorize_email(self, subject: str, body: str) -> list:
        """
        Categorize the email based on content.

        Args:
            subject: Email subject
            body: Email body

        Returns:
            List of categories
        """
        categories = []
        text = f"{subject} {body}".lower()

        category_keywords = {
            "legal": ["contract", "agreement", "legal", "court", "filing"],
            "financial": ["invoice", "payment", "budget", "financial", "billing"],
            "deadline": ["deadline", "due date", "by", "before"],
            "meeting": ["meeting", "call", "conference", "zoom", "schedule"],
            "document": ["document", "file", "attachment", "pdf", "signed"],
            "client": ["client", "customer", "matter"],
            "internal": ["team", "internal", "fyi", "update"]
        }

        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)

        return categories if categories else ["general"]

    def _requires_response(self, body: str) -> bool:
        """
        Determine if email requires a response.

        Args:
            body: Email body

        Returns:
            True if response needed, False otherwise
        """
        response_indicators = [
            "please respond",
            "let me know",
            "please confirm",
            "can you",
            "would you",
            "could you",
            "?",
            "please reply"
        ]

        body_lower = body.lower()
        return any(indicator in body_lower for indicator in response_indicators)

    def _generate_suggestions(self, analysis: Dict[str, Any]) -> list:
        """
        Generate suggested actions based on analysis.

        Args:
            analysis: Email analysis results

        Returns:
            List of suggested actions
        """
        suggestions = []

        # Priority-based suggestions
        if analysis["priority"] == "high":
            suggestions.append("Flag for immediate attention")

        if analysis["urgency"]["is_urgent"]:
            suggestions.append("Add to urgent task list")

        if analysis["urgency"]["deadlines_mentioned"] > 0:
            suggestions.append("Create calendar reminder for deadline")

        if analysis["requires_response"]:
            suggestions.append("Schedule time to compose response")

        if "legal" in analysis["categories"]:
            suggestions.append("Route to legal team for review")

        if len(analysis["action_items"]) > 0:
            suggestions.append(f"Create {len(analysis['action_items'])} tasks from action items")

        return suggestions

    def train(self, training_data: Dict[str, Any]):
        """
        Train the agent with historical email data.

        Args:
            training_data: Dictionary containing training information
                - sender_priorities: Dict mapping senders to priority levels
                - subject_patterns: Dict of common subject patterns
        """
        if "sender_priorities" in training_data:
            self.sender_priority_map.update(training_data["sender_priorities"])
            print(f"✓ Updated sender priorities: {len(training_data['sender_priorities'])} entries")

        if "subject_patterns" in training_data:
            self.subject_patterns.update(training_data["subject_patterns"])
            print(f"✓ Updated subject patterns: {len(training_data['subject_patterns'])} entries")

        self.training_data = training_data
        print(f"✓ {self.agent_name} training completed")
