"""
Event Bus - Pub/Sub Event Distribution System

Provides a publish-subscribe mechanism for system-wide event distribution,
enabling loose coupling between agents and components.
"""

from collections import defaultdict
from typing import Any, Callable, Dict, List
import asyncio
from datetime import datetime


class EventBus:
    """
    A publish-subscribe event bus for distributing events across the system.

    The EventBus enables loose coupling between components by allowing
    publishers to emit events without knowing who will consume them.
    """

    def __init__(self):
        """Initialize the event bus with empty subscriber lists."""
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_log: List[Dict[str, Any]] = []
        self._max_log_size = 10000

    def subscribe(self, event_type: str, callback: Callable):
        """
        Subscribe to a specific event type.

        Args:
            event_type: The type of event to subscribe to
            callback: Function to call when event is published
        """
        if not callable(callback):
            raise ValueError("Callback must be callable")

        self._subscribers[event_type].append(callback)
        print(f"✓ Subscribed to event: {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable):
        """
        Unsubscribe from a specific event type.

        Args:
            event_type: The type of event to unsubscribe from
            callback: The callback function to remove
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
                print(f"✓ Unsubscribed from event: {event_type}")
            except ValueError:
                print(f"⚠ Callback not found for event: {event_type}")

    def publish(self, event_type: str, payload: Any):
        """
        Publish an event to all subscribers.

        Args:
            event_type: The type of event being published
            payload: The event data
        """
        # Log the event
        self._log_event(event_type, payload)

        # Notify all subscribers
        subscribers = self._subscribers.get(event_type, [])

        for subscriber in subscribers:
            try:
                # Handle both sync and async callbacks
                if asyncio.iscoroutinefunction(subscriber):
                    asyncio.create_task(subscriber(payload))
                else:
                    subscriber(payload)
            except Exception as e:
                print(f"✗ Error in subscriber for {event_type}: {e}")

    async def publish_async(self, event_type: str, payload: Any):
        """
        Publish an event and wait for all async subscribers to complete.

        Args:
            event_type: The type of event being published
            payload: The event data
        """
        # Log the event
        self._log_event(event_type, payload)

        # Notify all subscribers
        subscribers = self._subscribers.get(event_type, [])
        tasks = []

        for subscriber in subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    tasks.append(subscriber(payload))
                else:
                    subscriber(payload)
            except Exception as e:
                print(f"✗ Error in subscriber for {event_type}: {e}")

        # Wait for all async tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def _log_event(self, event_type: str, payload: Any):
        """
        Log an event for debugging and auditing.

        Args:
            event_type: The type of event
            payload: The event data
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "payload_summary": self._summarize_payload(payload)
        }

        self._event_log.append(log_entry)

        # Trim log if it exceeds max size
        if len(self._event_log) > self._max_log_size:
            self._event_log = self._event_log[-self._max_log_size:]

    def _summarize_payload(self, payload: Any) -> str:
        """
        Create a summary of the payload for logging.

        Args:
            payload: The event payload

        Returns:
            String summary of the payload
        """
        if hasattr(payload, '__dict__'):
            return f"{type(payload).__name__} object"
        elif isinstance(payload, dict):
            return f"Dict with {len(payload)} keys"
        elif isinstance(payload, (list, tuple)):
            return f"{type(payload).__name__} with {len(payload)} items"
        else:
            return str(type(payload).__name__)

    def get_event_log(self, event_type: str = None, limit: int = 100) -> List[Dict]:
        """
        Retrieve the event log, optionally filtered by type.

        Args:
            event_type: Optional event type to filter by
            limit: Maximum number of events to return

        Returns:
            List of logged events
        """
        if event_type:
            filtered = [
                entry for entry in self._event_log
                if entry["event_type"] == event_type
            ]
            return filtered[-limit:]

        return self._event_log[-limit:]

    def get_subscriber_count(self, event_type: str = None) -> int:
        """
        Get the number of subscribers for an event type.

        Args:
            event_type: Optional event type to check

        Returns:
            Number of subscribers
        """
        if event_type:
            return len(self._subscribers.get(event_type, []))

        return sum(len(subs) for subs in self._subscribers.values())

    def get_event_types(self) -> List[str]:
        """
        Get all event types that have subscribers.

        Returns:
            List of event types
        """
        return list(self._subscribers.keys())

    def clear_subscribers(self, event_type: str = None):
        """
        Clear all subscribers, optionally for a specific event type.

        Args:
            event_type: Optional event type to clear subscribers for
        """
        if event_type:
            self._subscribers[event_type] = []
            print(f"✓ Cleared subscribers for: {event_type}")
        else:
            self._subscribers.clear()
            print("✓ Cleared all subscribers")
