"""
El Estratega - Process Learning Agent

Specializes in learning from workflows, detecting patterns, optimizing processes,
and providing strategic insights based on historical data.
"""

from typing import Any, Dict, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

from .base_agent import BaseAgent, AgentCapability


class ElEstratega(BaseAgent):
    """
    Process Learning Agent

    El Estratega analyzes workflow patterns, learns from historical data,
    identifies optimization opportunities, and provides strategic recommendations.
    """

    def __init__(self):
        """Initialize El Estratega with learning and analysis capabilities."""
        super().__init__("El Estratega")

        # Set agent capabilities
        self.set_capability(AgentCapability.PATTERN_LEARNING, True)

        # Pattern storage
        self.workflow_patterns: Dict[str, List[Dict]] = defaultdict(list)
        self.user_behavior_patterns: Dict[str, List[Dict]] = defaultdict(list)

        # Performance metrics
        self.process_metrics: Dict[str, Dict] = {}

        # Learning model data
        self.learned_rules: List[Dict] = []
        self.optimization_opportunities: List[Dict] = []

    async def process(self, event) -> Dict[str, Any]:
        """
        Process events for learning and pattern detection.

        Args:
            event: SystemEvent containing workflow or analysis data

        Returns:
            Dictionary with learning insights and recommendations
        """
        event_type = event.type

        if event_type == "document_uploaded":
            return await self._analyze_document_workflow(event)
        elif event_type == "document_analyzed":
            return await self._learn_from_analysis(event)
        elif event_type == "pattern_detected":
            return await self._process_pattern(event)
        else:
            # Learn from any event
            return await self._learn_from_event(event)

    async def _analyze_document_workflow(self, event) -> Dict[str, Any]:
        """
        Analyze document upload workflows to identify patterns.

        Args:
            event: Document upload event

        Returns:
            Workflow analysis results
        """
        doc_data = event.payload

        # Record workflow data
        workflow_data = {
            "timestamp": datetime.now().isoformat(),
            "document_type": doc_data.get("file_type"),
            "source": doc_data.get("source"),
            "time_to_process": doc_data.get("processing_time", 0),
            "user": doc_data.get("user_id")
        }

        # Store in pattern database
        workflow_key = f"{doc_data.get('source', 'unknown')}_{doc_data.get('file_type', 'unknown')}"
        self.workflow_patterns[workflow_key].append(workflow_data)

        # Analyze patterns if we have enough data
        insights = {}
        if len(self.workflow_patterns[workflow_key]) >= 10:
            insights = self._analyze_workflow_patterns(workflow_key)

        return {
            "agent": self.agent_name,
            "status": "processed",
            "timestamp": datetime.now().isoformat(),
            "workflow_recorded": True,
            "pattern_key": workflow_key,
            "total_samples": len(self.workflow_patterns[workflow_key]),
            "insights": insights,
            "recommendations": self._generate_workflow_recommendations(workflow_key)
        }

    async def _learn_from_analysis(self, event) -> Dict[str, Any]:
        """
        Learn from document analysis results.

        Args:
            event: Document analysis event

        Returns:
            Learning results
        """
        analysis_data = event.payload

        # Extract learning data
        doc_type = analysis_data.get("document_type")
        entities = analysis_data.get("entities", [])
        metadata = analysis_data.get("metadata", {})

        # Build pattern
        pattern = {
            "timestamp": datetime.now().isoformat(),
            "document_type": doc_type,
            "entity_count": len(entities),
            "entity_types": Counter([e.get("type") for e in entities]),
            "metadata_fields": list(metadata.keys())
        }

        # Store pattern
        self.workflow_patterns[f"analysis_{doc_type}"].append(pattern)

        # Detect if this reveals a new pattern
        new_pattern = self._detect_new_pattern(pattern)

        return {
            "agent": self.agent_name,
            "status": "processed",
            "timestamp": datetime.now().isoformat(),
            "pattern_learned": True,
            "new_pattern_detected": new_pattern is not None,
            "new_pattern": new_pattern
        }

    async def _process_pattern(self, event) -> Dict[str, Any]:
        """
        Process a detected pattern event.

        Args:
            event: Pattern detection event

        Returns:
            Pattern processing results
        """
        pattern_data = event.payload

        # Validate and store the pattern
        pattern_type = pattern_data.get("type")
        confidence = pattern_data.get("confidence", 0)

        if confidence > 0.7:
            # High confidence pattern - create a learned rule
            rule = {
                "type": pattern_type,
                "pattern": pattern_data.get("pattern"),
                "confidence": confidence,
                "created": datetime.now().isoformat(),
                "times_confirmed": 1
            }

            self.learned_rules.append(rule)

            return {
                "agent": self.agent_name,
                "status": "processed",
                "timestamp": datetime.now().isoformat(),
                "rule_created": True,
                "rule": rule
            }

        return {
            "agent": self.agent_name,
            "status": "processed",
            "timestamp": datetime.now().isoformat(),
            "rule_created": False,
            "reason": "Confidence threshold not met"
        }

    async def _learn_from_event(self, event) -> Dict[str, Any]:
        """
        Learn from general system events.

        Args:
            event: Any system event

        Returns:
            Learning results
        """
        # Record event for pattern analysis
        event_pattern = {
            "type": event.type,
            "timestamp": event.timestamp,
            "priority": event.priority,
            "agent_origin": str(event.agent_origin) if event.agent_origin else None
        }

        # Store in general patterns
        self.workflow_patterns["system_events"].append(event_pattern)

        # Analyze temporal patterns
        temporal_insights = self._analyze_temporal_patterns()

        return {
            "agent": self.agent_name,
            "status": "processed",
            "timestamp": datetime.now().isoformat(),
            "event_recorded": True,
            "temporal_insights": temporal_insights
        }

    def _analyze_workflow_patterns(self, workflow_key: str) -> Dict[str, Any]:
        """
        Analyze patterns in a specific workflow.

        Args:
            workflow_key: Key identifying the workflow

        Returns:
            Pattern analysis insights
        """
        patterns = self.workflow_patterns[workflow_key]

        if not patterns:
            return {}

        # Calculate metrics
        processing_times = [p.get("time_to_process", 0) for p in patterns if p.get("time_to_process")]

        insights = {
            "total_instances": len(patterns),
            "unique_users": len(set(p.get("user") for p in patterns if p.get("user"))),
            "most_common_source": self._get_most_common(patterns, "source")
        }

        if processing_times:
            insights["processing_time"] = {
                "average": statistics.mean(processing_times),
                "median": statistics.median(processing_times),
                "min": min(processing_times),
                "max": max(processing_times)
            }

        # Detect time-of-day patterns
        timestamps = [p.get("timestamp") for p in patterns if p.get("timestamp")]
        insights["time_patterns"] = self._analyze_time_patterns(timestamps)

        return insights

    def _get_most_common(self, patterns: List[Dict], field: str) -> Any:
        """
        Get the most common value for a field in patterns.

        Args:
            patterns: List of pattern dictionaries
            field: Field to analyze

        Returns:
            Most common value
        """
        values = [p.get(field) for p in patterns if p.get(field)]
        if not values:
            return None

        counter = Counter(values)
        return counter.most_common(1)[0][0] if counter else None

    def _analyze_time_patterns(self, timestamps: List[str]) -> Dict[str, Any]:
        """
        Analyze temporal patterns in timestamps.

        Args:
            timestamps: List of ISO format timestamps

        Returns:
            Temporal pattern analysis
        """
        if not timestamps:
            return {}

        hours = []
        days_of_week = []

        for ts in timestamps:
            try:
                dt = datetime.fromisoformat(ts)
                hours.append(dt.hour)
                days_of_week.append(dt.weekday())
            except Exception:
                continue

        hour_distribution = Counter(hours)
        day_distribution = Counter(days_of_week)

        return {
            "most_active_hour": hour_distribution.most_common(1)[0][0] if hour_distribution else None,
            "most_active_day": day_distribution.most_common(1)[0][0] if day_distribution else None,
            "hour_distribution": dict(hour_distribution),
            "day_distribution": dict(day_distribution)
        }

    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
        """
        Analyze temporal patterns across all events.

        Returns:
            Temporal pattern insights
        """
        system_events = self.workflow_patterns.get("system_events", [])

        if len(system_events) < 10:
            return {"status": "insufficient_data"}

        # Analyze event frequency
        recent_events = [
            e for e in system_events[-100:]
            if datetime.fromisoformat(e["timestamp"]) > datetime.now() - timedelta(hours=24)
        ]

        event_types = Counter([e["type"] for e in recent_events])

        return {
            "events_last_24h": len(recent_events),
            "most_common_event": event_types.most_common(1)[0] if event_types else None,
            "event_distribution": dict(event_types.most_common(5))
        }

    def _detect_new_pattern(self, pattern: Dict) -> Optional[Dict]:
        """
        Detect if a pattern represents something new.

        Args:
            pattern: Pattern data

        Returns:
            New pattern details if detected, None otherwise
        """
        doc_type = pattern.get("document_type")
        similar_patterns = self.workflow_patterns.get(f"analysis_{doc_type}", [])

        if len(similar_patterns) < 5:
            return None

        # Compare entity types with historical patterns
        current_entities = set(pattern.get("entity_types", {}).keys())
        historical_entities = [
            set(p.get("entity_types", {}).keys())
            for p in similar_patterns[-10:]
        ]

        # Check for new entity types
        all_historical = set().union(*historical_entities) if historical_entities else set()
        new_entities = current_entities - all_historical

        if new_entities:
            return {
                "type": "new_entity_types",
                "document_type": doc_type,
                "new_entities": list(new_entities),
                "confidence": 0.8
            }

        return None

    def _generate_workflow_recommendations(self, workflow_key: str) -> List[str]:
        """
        Generate recommendations for workflow optimization.

        Args:
            workflow_key: Workflow identifier

        Returns:
            List of recommendations
        """
        recommendations = []

        patterns = self.workflow_patterns.get(workflow_key, [])

        if not patterns:
            return recommendations

        # Analyze processing times
        processing_times = [p.get("time_to_process", 0) for p in patterns if p.get("time_to_process")]

        if processing_times and len(processing_times) >= 5:
            avg_time = statistics.mean(processing_times)
            max_time = max(processing_times)

            if max_time > avg_time * 2:
                recommendations.append(
                    f"Investigate slow processing instances (max: {max_time:.2f}s vs avg: {avg_time:.2f}s)"
                )

        # Check for automation opportunities
        if len(patterns) > 20:
            recommendations.append(
                f"High volume workflow ({len(patterns)} instances) - consider automation"
            )

        # Time-based recommendations
        insights = self._analyze_workflow_patterns(workflow_key)
        time_patterns = insights.get("time_patterns", {})

        if time_patterns.get("most_active_hour"):
            hour = time_patterns["most_active_hour"]
            recommendations.append(
                f"Peak activity at {hour}:00 - consider resource allocation"
            )

        return recommendations

    def get_learning_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all learned patterns and rules.

        Returns:
            Learning summary
        """
        return {
            "total_workflow_patterns": len(self.workflow_patterns),
            "total_learned_rules": len(self.learned_rules),
            "optimization_opportunities": len(self.optimization_opportunities),
            "workflow_categories": list(self.workflow_patterns.keys()),
            "top_rules": self.learned_rules[:10],
            "recent_optimizations": self.optimization_opportunities[-5:]
        }

    def suggest_optimizations(self) -> List[Dict[str, Any]]:
        """
        Generate optimization suggestions based on learned patterns.

        Returns:
            List of optimization suggestions
        """
        suggestions = []

        # Analyze all workflows for optimization opportunities
        for workflow_key, patterns in self.workflow_patterns.items():
            if len(patterns) >= 10:
                recommendations = self._generate_workflow_recommendations(workflow_key)

                if recommendations:
                    suggestions.append({
                        "workflow": workflow_key,
                        "pattern_count": len(patterns),
                        "recommendations": recommendations,
                        "priority": "high" if len(patterns) > 50 else "medium"
                    })

        return suggestions

    def train(self, training_data: Dict[str, Any]):
        """
        Train the agent with historical workflow data.

        Args:
            training_data: Dictionary containing:
                - historical_workflows: Historical workflow data
                - known_patterns: Pre-identified patterns
                - optimization_rules: Known optimization rules
        """
        if "historical_workflows" in training_data:
            for workflow_key, patterns in training_data["historical_workflows"].items():
                self.workflow_patterns[workflow_key].extend(patterns)
            print(f"✓ Loaded historical workflows: {len(training_data['historical_workflows'])} types")

        if "known_patterns" in training_data:
            self.learned_rules.extend(training_data["known_patterns"])
            print(f"✓ Loaded known patterns: {len(training_data['known_patterns'])} patterns")

        if "optimization_rules" in training_data:
            self.optimization_opportunities.extend(training_data["optimization_rules"])
            print(f"✓ Loaded optimization rules: {len(training_data['optimization_rules'])} rules")

        self.training_data = training_data
        print(f"✓ {self.agent_name} training completed")
