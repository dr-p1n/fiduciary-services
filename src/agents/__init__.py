"""
AGENTTA Agents Module

This module contains all specialized agents that power the AGENTTA system.
"""

from .base_agent import BaseAgent, AgentCapability
from .la_secretaria import LaSecretaria
from .el_calendista import ElCalendista
from .la_archivista import LaArchivista
from .el_estratega import ElEstratega

__all__ = [
    "BaseAgent",
    "AgentCapability",
    "LaSecretaria",
    "ElCalendista",
    "LaArchivista",
    "ElEstratega"
]
