"""
Shared Context Manager - System-wide State Management

Provides thread-safe shared state management across agents and components,
enabling collaborative intelligence and information sharing.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, Optional, List
from threading import Lock


class SharedContextManager:
    """
    Manages shared context and state across the AGENTTA system.

    The SharedContextManager provides a centralized, thread-safe storage
    for system-wide state that can be accessed and modified by any agent
    or component.
    """

    def __init__(self):
        """Initialize the shared context with thread-safe storage."""
        self._context: Dict[str, Any] = {}
        self._lock = Lock()
        self._history: List[Dict[str, Any]] = []
        self._max_history_size = 1000

    def update(self, new_data: Dict[str, Any]):
        """
        Update the shared context with new data.

        Args:
            new_data: Dictionary of new data to merge into context
        """
        with self._lock:
            old_keys = set(self._context.keys())
            self._context.update(new_data)
            new_keys = set(new_data.keys())

            # Log the update
            self._log_update(new_keys, old_keys)

    def set(self, key: str, value: Any):
        """
        Set a specific key in the context.

        Args:
            key: The key to set
            value: The value to store
        """
        with self._lock:
            old_value = self._context.get(key)
            self._context[key] = value

            # Log the change
            self._log_change(key, old_value, value)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from the context.

        Args:
            key: The key to retrieve
            default: Default value if key doesn't exist

        Returns:
            The value associated with the key, or default if not found
        """
        with self._lock:
            return self._context.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """
        Retrieve all context data.

        Returns:
            Copy of the entire context dictionary
        """
        with self._lock:
            return self._context.copy()

    def delete(self, key: str) -> bool:
        """
        Delete a key from the context.

        Args:
            key: The key to delete

        Returns:
            True if key was deleted, False if key didn't exist
        """
        with self._lock:
            if key in self._context:
                value = self._context.pop(key)
                self._log_deletion(key, value)
                return True
            return False

    def has(self, key: str) -> bool:
        """
        Check if a key exists in the context.

        Args:
            key: The key to check

        Returns:
            True if key exists, False otherwise
        """
        with self._lock:
            return key in self._context

    def clear(self):
        """Clear all context data."""
        with self._lock:
            self._context.clear()
            self._log_clear()
            print("✓ Shared context cleared")

    def keys(self) -> List[str]:
        """
        Get all keys in the context.

        Returns:
            List of all context keys
        """
        with self._lock:
            return list(self._context.keys())

    def size(self) -> int:
        """
        Get the number of items in the context.

        Returns:
            Number of context items
        """
        with self._lock:
            return len(self._context)

    def get_namespace(self, namespace: str) -> Dict[str, Any]:
        """
        Get all keys that start with a specific namespace prefix.

        Args:
            namespace: The namespace prefix (e.g., 'agent:secretaria')

        Returns:
            Dictionary of keys and values in the namespace
        """
        with self._lock:
            prefix = f"{namespace}:"
            return {
                key: value
                for key, value in self._context.items()
                if key.startswith(prefix)
            }

    def set_namespaced(self, namespace: str, key: str, value: Any):
        """
        Set a value in a specific namespace.

        Args:
            namespace: The namespace (e.g., 'agent:secretaria')
            key: The key within the namespace
            value: The value to store
        """
        full_key = f"{namespace}:{key}"
        self.set(full_key, value)

    def get_namespaced(self, namespace: str, key: str, default: Any = None) -> Any:
        """
        Get a value from a specific namespace.

        Args:
            namespace: The namespace (e.g., 'agent:secretaria')
            key: The key within the namespace
            default: Default value if key doesn't exist

        Returns:
            The value or default
        """
        full_key = f"{namespace}:{key}"
        return self.get(full_key, default)

    def _log_update(self, new_keys: set, old_keys: set):
        """
        Log a context update to history.

        Args:
            new_keys: Set of keys being updated
            old_keys: Set of keys that existed before update
        """
        added_keys = new_keys - old_keys
        updated_keys = new_keys & old_keys

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "update",
            "added_keys": list(added_keys),
            "updated_keys": list(updated_keys),
            "total_keys": len(self._context)
        }

        self._add_to_history(log_entry)

    def _log_change(self, key: str, old_value: Any, new_value: Any):
        """
        Log a single key change.

        Args:
            key: The key that changed
            old_value: The previous value
            new_value: The new value
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "set",
            "key": key,
            "had_previous_value": old_value is not None
        }

        self._add_to_history(log_entry)

    def _log_deletion(self, key: str, value: Any):
        """
        Log a key deletion.

        Args:
            key: The key that was deleted
            value: The value that was deleted
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "delete",
            "key": key
        }

        self._add_to_history(log_entry)

    def _log_clear(self):
        """Log a context clear operation."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "clear",
            "keys_cleared": len(self._context)
        }

        self._add_to_history(log_entry)

    def _add_to_history(self, log_entry: Dict[str, Any]):
        """
        Add an entry to the history log.

        Args:
            log_entry: The log entry to add
        """
        self._history.append(log_entry)

        # Trim history if needed
        if len(self._history) > self._max_history_size:
            self._history = self._history[-self._max_history_size:]

    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the context change history.

        Args:
            limit: Maximum number of history entries to return

        Returns:
            List of history entries
        """
        with self._lock:
            return self._history[-limit:]

    def export_to_json(self) -> str:
        """
        Export the context to a JSON string.

        Returns:
            JSON string representation of the context
        """
        with self._lock:
            return json.dumps(self._context, indent=2, default=str)

    def import_from_json(self, json_str: str):
        """
        Import context from a JSON string.

        Args:
            json_str: JSON string to import
        """
        try:
            data = json.loads(json_str)
            self.update(data)
            print(f"✓ Imported {len(data)} keys from JSON")
        except json.JSONDecodeError as e:
            print(f"✗ Failed to import JSON: {e}")
