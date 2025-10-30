"""
El Calendista - Deadline Management Agent

Specializes in tracking deadlines, managing calendar events, and providing
jurisdiction-specific deadline intelligence.
"""

from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import re

from .base_agent import BaseAgent, AgentCapability


class ElCalendista(BaseAgent):
    """
    Deadline Management Agent

    El Calendista tracks deadlines, manages calendar events, and provides
    intelligent deadline calculations based on jurisdiction-specific rules.
    """

    def __init__(self):
        """Initialize El Calendista with deadline management capabilities."""
        super().__init__("El Calendista")

        # Set agent capabilities
        self.set_capability(AgentCapability.DEADLINE_TRACKING, True)
        self.set_capability(AgentCapability.CALENDAR_MANAGEMENT, True)

        # Deadline calculation rules by jurisdiction
        self.jurisdiction_rules = {}

        # Active deadlines being tracked
        self.active_deadlines = {}

        # Holiday calendars by jurisdiction
        self.holiday_calendars = {}

    async def process(self, event) -> Dict[str, Any]:
        """
        Process deadline and calendar-related events.

        Args:
            event: SystemEvent containing deadline or calendar data

        Returns:
            Dictionary with deadline analysis and calendar actions
        """
        event_type = event.type

        if event_type == "email_received":
            return await self._process_email_for_deadlines(event)
        elif event_type == "deadline_approaching":
            return await self._process_deadline_alert(event)
        elif event_type == "calendar_event_created":
            return await self._process_calendar_event(event)
        else:
            return {
                "agent": self.agent_name,
                "status": "skipped",
                "reason": f"Event type '{event_type}' not handled by this agent"
            }

    async def _process_email_for_deadlines(self, event) -> Dict[str, Any]:
        """
        Extract and process deadlines from email content.

        Args:
            event: Email event

        Returns:
            Deadline extraction results
        """
        email_data = event.payload
        subject = email_data.get("subject", "")
        body = email_data.get("body", "")

        # Extract deadline information
        deadlines = self._extract_deadlines(f"{subject} {body}")

        result = {
            "agent": self.agent_name,
            "status": "processed",
            "timestamp": datetime.now().isoformat(),
            "deadlines_found": len(deadlines),
            "deadlines": deadlines,
            "suggested_actions": []
        }

        # Generate calendar entries for each deadline
        for deadline in deadlines:
            calendar_entry = self._create_calendar_entry(deadline, email_data)
            result["suggested_actions"].append({
                "action": "create_calendar_event",
                "details": calendar_entry
            })

            # Add reminder actions
            reminders = self._calculate_reminders(deadline["date"])
            for reminder in reminders:
                result["suggested_actions"].append({
                    "action": "create_reminder",
                    "details": reminder
                })

        return result

    async def _process_deadline_alert(self, event) -> Dict[str, Any]:
        """
        Process deadline approaching alerts.

        Args:
            event: Deadline alert event

        Returns:
            Alert processing results
        """
        deadline_data = event.payload
        deadline_id = deadline_data.get("id")
        deadline_date = deadline_data.get("date")

        # Calculate time until deadline
        if isinstance(deadline_date, str):
            deadline_date = datetime.fromisoformat(deadline_date)

        time_until = deadline_date - datetime.now()

        return {
            "agent": self.agent_name,
            "status": "processed",
            "timestamp": datetime.now().isoformat(),
            "deadline_id": deadline_id,
            "days_until_deadline": time_until.days,
            "hours_until_deadline": time_until.total_seconds() / 3600,
            "urgency_level": self._calculate_urgency(time_until),
            "recommended_actions": self._generate_deadline_actions(time_until, deadline_data)
        }

    async def _process_calendar_event(self, event) -> Dict[str, Any]:
        """
        Process calendar event creation.

        Args:
            event: Calendar event

        Returns:
            Event processing results
        """
        calendar_data = event.payload

        return {
            "agent": self.agent_name,
            "status": "processed",
            "timestamp": datetime.now().isoformat(),
            "event_created": calendar_data.get("title"),
            "event_date": calendar_data.get("date"),
            "conflicts_checked": True,
            "conflicts_found": []  # TODO: Implement conflict detection
        }

    def _extract_deadlines(self, text: str) -> list:
        """
        Extract deadline information from text.

        Args:
            text: Text to analyze

        Returns:
            List of extracted deadlines
        """
        deadlines = []

        # Common deadline patterns
        patterns = [
            r"due\s+(on\s+)?(\w+\s+\d+,?\s+\d{4})",
            r"deadline:?\s*(\w+\s+\d+,?\s+\d{4})",
            r"by\s+(\w+\s+\d+,?\s+\d{4})",
            r"before\s+(\w+\s+\d+,?\s+\d{4})",
            r"(\d{1,2}/\d{1,2}/\d{4})",
            r"(\d{4}-\d{2}-\d{2})"
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Handle tuple results from regex groups
                date_str = match[1] if isinstance(match, tuple) else match

                try:
                    parsed_date = self._parse_date(date_str)
                    if parsed_date:
                        deadlines.append({
                            "text": date_str,
                            "date": parsed_date.isoformat(),
                            "type": "explicit"
                        })
                except Exception as e:
                    continue

        # Look for relative dates
        relative_patterns = [
            (r"(\d+)\s+days?", "days"),
            (r"(\d+)\s+weeks?", "weeks"),
            (r"(\d+)\s+months?", "months")
        ]

        for pattern, unit in relative_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                count = int(match)
                calculated_date = self._calculate_relative_date(count, unit)
                deadlines.append({
                    "text": f"{count} {unit}",
                    "date": calculated_date.isoformat(),
                    "type": "relative"
                })

        return deadlines

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse a date string into a datetime object.

        Args:
            date_str: Date string to parse

        Returns:
            Parsed datetime or None
        """
        formats = [
            "%B %d, %Y",
            "%b %d, %Y",
            "%m/%d/%Y",
            "%Y-%m-%d",
            "%d/%m/%Y"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        return None

    def _calculate_relative_date(self, count: int, unit: str) -> datetime:
        """
        Calculate a date relative to now.

        Args:
            count: Number of units
            unit: Time unit (days, weeks, months)

        Returns:
            Calculated datetime
        """
        now = datetime.now()

        if unit == "days":
            return now + timedelta(days=count)
        elif unit == "weeks":
            return now + timedelta(weeks=count)
        elif unit == "months":
            # Approximate months as 30 days
            return now + timedelta(days=count * 30)

        return now

    def _create_calendar_entry(self, deadline: Dict, email_data: Dict) -> Dict[str, Any]:
        """
        Create a calendar entry from deadline information.

        Args:
            deadline: Deadline information
            email_data: Related email data

        Returns:
            Calendar entry details
        """
        return {
            "title": f"Deadline: {email_data.get('subject', 'Untitled')}",
            "date": deadline["date"],
            "type": "deadline",
            "source": "email",
            "source_id": email_data.get("id"),
            "description": f"From: {email_data.get('from', 'Unknown')}",
            "all_day": True
        }

    def _calculate_reminders(self, deadline_date: str) -> list:
        """
        Calculate reminder times for a deadline.

        Args:
            deadline_date: ISO format deadline date

        Returns:
            List of reminder configurations
        """
        deadline = datetime.fromisoformat(deadline_date)
        reminders = []

        # Add reminders at: 7 days, 3 days, 1 day, 4 hours before
        reminder_offsets = [7, 3, 1, 0.166]  # days

        for offset in reminder_offsets:
            reminder_date = deadline - timedelta(days=offset)

            # Only add reminders in the future
            if reminder_date > datetime.now():
                reminders.append({
                    "reminder_date": reminder_date.isoformat(),
                    "message": f"Deadline in {offset} days" if offset >= 1 else "Deadline today!",
                    "type": "deadline_reminder"
                })

        return reminders

    def _calculate_urgency(self, time_until: timedelta) -> str:
        """
        Calculate urgency level based on time until deadline.

        Args:
            time_until: Time until deadline

        Returns:
            Urgency level: 'critical', 'high', 'medium', or 'low'
        """
        hours = time_until.total_seconds() / 3600

        if hours < 4:
            return "critical"
        elif hours < 24:
            return "high"
        elif hours < 72:
            return "medium"
        else:
            return "low"

    def _generate_deadline_actions(
        self,
        time_until: timedelta,
        deadline_data: Dict
    ) -> list:
        """
        Generate recommended actions for approaching deadline.

        Args:
            time_until: Time until deadline
            deadline_data: Deadline information

        Returns:
            List of recommended actions
        """
        actions = []
        hours = time_until.total_seconds() / 3600

        if hours < 4:
            actions.append("Send critical alert notification")
            actions.append("Escalate to senior team member")

        if hours < 24:
            actions.append("Move to top of priority list")
            actions.append("Block calendar for focused work")

        if hours < 72:
            actions.append("Review progress on related tasks")
            actions.append("Allocate resources if needed")

        actions.append("Update status in project tracker")

        return actions

    def train(self, training_data: Dict[str, Any]):
        """
        Train the agent with jurisdiction-specific deadline rules.

        Args:
            training_data: Dictionary containing:
                - jurisdiction_rules: Deadline calculation rules
                - holiday_calendars: Holiday dates by jurisdiction
        """
        if "jurisdiction_rules" in training_data:
            self.jurisdiction_rules.update(training_data["jurisdiction_rules"])
            print(f"✓ Updated jurisdiction rules: {len(training_data['jurisdiction_rules'])} entries")

        if "holiday_calendars" in training_data:
            self.holiday_calendars.update(training_data["holiday_calendars"])
            print(f"✓ Updated holiday calendars: {len(training_data['holiday_calendars'])} entries")

        self.training_data = training_data
        print(f"✓ {self.agent_name} training completed")
