"""
IMPROVEMENTS #7, #8, #9: Analytics, A/B Testing, and Smart Scheduling
Advanced features for optimization and automation
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import random


# ============================================================================
# IMPROVEMENT #7: Performance Analytics and Reporting
# ============================================================================

@dataclass
class PerformanceMetrics:
    """Performance metrics for analytics"""
    metric_name: str
    value: float
    target: Optional[float] = None
    variance: Optional[float] = None
    trend: str = "stable"  # up, down, stable
    period: str = "day"


class AnalyticsEngine:
    """
    Comprehensive analytics and reporting system

    Tracks:
    - Conversion rates by stage
    - Agent performance
    - Revenue pipeline
    - Time-to-close metrics
    - Success factors
    """

    def __init__(self):
        self.opportunities: List[Dict] = []
        self.interactions: List[Dict] = []
        self.conversions: Dict[str, List[Dict]] = defaultdict(list)

    def track_opportunity(self, opportunity: Dict[str, Any]):
        """Track opportunity for analytics"""
        self.opportunities.append({
            **opportunity,
            "tracked_at": datetime.now().isoformat()
        })

    def track_stage_conversion(
        self,
        opportunity_id: str,
        from_stage: str,
        to_stage: str,
        success: bool,
        duration_seconds: float
    ):
        """Track stage conversion"""
        self.conversions[from_stage].append({
            "opportunity_id": opportunity_id,
            "to_stage": to_stage,
            "success": success,
            "duration": duration_seconds,
            "timestamp": datetime.now().isoformat()
        })

    def get_conversion_funnel(self) -> Dict[str, Any]:
        """Calculate conversion funnel metrics"""

        stages = [
            "prospecting",
            "qualified",
            "researched",
            "use_case_built",
            "serviceability_confirmed",
            "pricing_complete",
            "ready_for_outreach",
            "contacted",
            "engaged",
            "opportunity",
            "closed_won"
        ]

        funnel = {}
        stage_counts = defaultdict(int)

        # Count opportunities at each stage
        for opp in self.opportunities:
            stage = opp.get("stage", "unknown")
            stage_counts[stage] += 1

        # Calculate conversion rates
        total_entered = len(self.opportunities)

        for i, stage in enumerate(stages):
            count = stage_counts.get(stage, 0)

            funnel[stage] = {
                "count": count,
                "percentage_of_total": (count / total_entered * 100) if total_entered > 0 else 0,
                "conversion_from_previous": self._calc_stage_conversion(stages, i, stage_counts)
            }

        return funnel

    def _calc_stage_conversion(
        self,
        stages: List[str],
        current_index: int,
        stage_counts: Dict
    ) -> float:
        """Calculate conversion rate from previous stage"""

        if current_index == 0:
            return 100.0  # First stage

        previous_stage = stages[current_index - 1]
        current_stage = stages[current_index]

        prev_count = stage_counts.get(previous_stage, 0)
        curr_count = stage_counts.get(current_stage, 0)

        if prev_count == 0:
            return 0.0

        return (curr_count / prev_count) * 100

    def get_agent_performance(self) -> List[Dict[str, Any]]:
        """Analyze agent performance metrics"""

        agent_stats = defaultdict(lambda: {
            "tasks_completed": 0,
            "successes": 0,
            "failures": 0,
            "avg_processing_time": [],
            "total_tokens": 0
        })

        # Aggregate stats (would pull from agent manager in production)
        # This is a placeholder

        return [
            {
                "agent_name": agent,
                "success_rate": stats["successes"] / max(stats["tasks_completed"], 1),
                "avg_time": statistics.mean(stats["avg_processing_time"]) if stats["avg_processing_time"] else 0,
                "total_tokens": stats["total_tokens"]
            }
            for agent, stats in agent_stats.items()
        ]

    def get_revenue_metrics(self) -> Dict[str, float]:
        """Calculate revenue pipeline metrics"""

        total_pipeline = sum(
            opp.get("estimated_deal_value", 0)
            for opp in self.opportunities
        )

        weighted_pipeline = sum(
            opp.get("estimated_deal_value", 0) * opp.get("close_probability", 0)
            for opp in self.opportunities
        )

        won_revenue = sum(
            opp.get("estimated_deal_value", 0)
            for opp in self.opportunities
            if opp.get("stage") == "closed_won"
        )

        return {
            "total_pipeline_value": total_pipeline,
            "weighted_pipeline": weighted_pipeline,
            "won_revenue": won_revenue,
            "win_rate": self._calculate_win_rate()
        }

    def _calculate_win_rate(self) -> float:
        """Calculate overall win rate"""

        closed_opps = [
            opp for opp in self.opportunities
            if opp.get("stage") in ["closed_won", "closed_lost"]
        ]

        if not closed_opps:
            return 0.0

        won = sum(1 for opp in closed_opps if opp.get("stage") == "closed_won")
        return (won / len(closed_opps)) * 100

    def get_time_to_close_metrics(self) -> Dict[str, float]:
        """Analyze time-to-close metrics"""

        won_opps = [
            opp for opp in self.opportunities
            if opp.get("stage") == "closed_won" and "created_at" in opp and "closed_at" in opp
        ]

        if not won_opps:
            return {"avg_days": 0, "median_days": 0}

        durations = []
        for opp in won_opps:
            created = datetime.fromisoformat(opp["created_at"])
            closed = datetime.fromisoformat(opp["closed_at"])
            days = (closed - created).days
            durations.append(days)

        return {
            "avg_days_to_close": statistics.mean(durations),
            "median_days_to_close": statistics.median(durations),
            "min_days": min(durations),
            "max_days": max(durations)
        }

    def generate_report(self, report_type: str = "weekly") -> Dict[str, Any]:
        """Generate comprehensive analytics report"""

        return {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "conversion_funnel": self.get_conversion_funnel(),
            "agent_performance": self.get_agent_performance(),
            "revenue_metrics": self.get_revenue_metrics(),
            "time_metrics": self.get_time_to_close_metrics(),
            "total_opportunities": len(self.opportunities)
        }


# ============================================================================
# IMPROVEMENT #8: A/B Testing Framework
# ============================================================================

@dataclass
class ABTestVariant:
    """A/B test variant configuration"""
    variant_id: str
    variant_name: str
    config: Dict[str, Any]
    traffic_percentage: float  # 0-100


class ABTestFramework:
    """
    A/B testing framework for optimization

    Test variables:
    - Email subject lines
    - Outreach messaging
    - Pricing presentation
    - Use case emphasis
    - Follow-up timing
    """

    def __init__(self):
        self.active_tests: Dict[str, List[ABTestVariant]] = {}
        self.results: Dict[str, List[Dict]] = defaultdict(list)

    def create_test(
        self,
        test_name: str,
        variants: List[ABTestVariant],
        success_metric: str
    ):
        """
        Create A/B test

        Example:
        test = ABTestFramework()
        test.create_test(
            "email_subject_test",
            variants=[
                ABTestVariant("A", "ROI-focused", {"subject": "Save 50% on EDI"}, 50),
                ABTestVariant("B", "Pain-focused", {"subject": "Fix EDI Problems"}, 50)
            ],
            success_metric="open_rate"
        )
        """

        # Validate traffic allocation
        total_traffic = sum(v.traffic_percentage for v in variants)
        if abs(total_traffic - 100) > 0.01:
            raise ValueError(f"Traffic must sum to 100%, got {total_traffic}%")

        self.active_tests[test_name] = {
            "variants": variants,
            "success_metric": success_metric,
            "created_at": datetime.now()
        }

    def get_variant(self, test_name: str, user_id: str) -> Optional[ABTestVariant]:
        """
        Get variant assignment for user

        Uses consistent hashing for stable assignments
        """

        if test_name not in self.active_tests:
            return None

        test = self.active_tests[test_name]
        variants = test["variants"]

        # Simple hash-based assignment (consistent per user)
        hash_val = hash(f"{test_name}:{user_id}") % 100

        cumulative = 0
        for variant in variants:
            cumulative += variant.traffic_percentage
            if hash_val < cumulative:
                return variant

        return variants[-1]  # Fallback

    def track_result(
        self,
        test_name: str,
        variant_id: str,
        success: bool,
        metric_value: Optional[float] = None
    ):
        """Track A/B test result"""

        self.results[test_name].append({
            "variant_id": variant_id,
            "success": success,
            "metric_value": metric_value,
            "timestamp": datetime.now().isoformat()
        })

    def get_test_results(self, test_name: str) -> Dict[str, Any]:
        """Analyze A/B test results"""

        if test_name not in self.results:
            return {"error": "No results yet"}

        results_by_variant = defaultdict(list)

        for result in self.results[test_name]:
            results_by_variant[result["variant_id"]].append(result)

        analysis = {}
        for variant_id, results in results_by_variant.items():
            successes = sum(1 for r in results if r["success"])
            total = len(results)

            analysis[variant_id] = {
                "total_samples": total,
                "successes": successes,
                "success_rate": (successes / total * 100) if total > 0 else 0,
                "avg_metric_value": statistics.mean(
                    [r["metric_value"] for r in results if r["metric_value"] is not None]
                ) if any(r["metric_value"] is not None for r in results) else None
            }

        # Determine winner
        winner = max(
            analysis.items(),
            key=lambda x: x[1]["success_rate"]
        )

        return {
            "test_name": test_name,
            "variant_analysis": analysis,
            "recommended_winner": winner[0],
            "confidence": self._calculate_confidence(analysis)
        }

    def _calculate_confidence(self, analysis: Dict) -> float:
        """Calculate statistical confidence (simplified)"""

        # In production, use proper statistical tests (t-test, chi-square)
        # This is a simplified placeholder

        variant_rates = [v["success_rate"] for v in analysis.values()]

        if len(variant_rates) < 2:
            return 0.0

        # Simple confidence based on sample size and difference
        max_rate = max(variant_rates)
        min_rate = min(variant_rates)
        difference = max_rate - min_rate

        total_samples = sum(v["total_samples"] for v in analysis.values())

        # Rough confidence score
        confidence = min(95, (difference / 10) * (total_samples / 100))

        return confidence


# ============================================================================
# IMPROVEMENT #9: Intelligent Scheduling and Follow-up System
# ============================================================================

class SmartScheduler:
    """
    Intelligent scheduling for follow-ups and tasks

    Features:
    - Optimal timing based on engagement patterns
    - Automatic retry logic
    - Priority-based scheduling
    - Time zone awareness
    """

    def __init__(self):
        self.scheduled_tasks: List[Dict] = []
        self.engagement_patterns: Dict[str, List[datetime]] = defaultdict(list)

    def schedule_follow_up(
        self,
        prospect_id: str,
        task_type: str,
        base_delay_days: int,
        priority: int = 5
    ) -> Dict[str, Any]:
        """
        Schedule intelligent follow-up

        Args:
            prospect_id: Prospect identifier
            task_type: Type of follow-up (email, call, etc.)
            base_delay_days: Base delay in days
            priority: 1-10 priority

        Returns:
            Scheduled task details
        """

        # Calculate optimal time based on engagement patterns
        optimal_time = self._calculate_optimal_time(
            prospect_id,
            base_delay_days
        )

        task = {
            "task_id": f"task_{int(datetime.now().timestamp())}",
            "prospect_id": prospect_id,
            "task_type": task_type,
            "scheduled_for": optimal_time,
            "priority": priority,
            "status": "scheduled",
            "created_at": datetime.now()
        }

        self.scheduled_tasks.append(task)
        return task

    def _calculate_optimal_time(
        self,
        prospect_id: str,
        base_delay_days: int
    ) -> datetime:
        """Calculate optimal follow-up time"""

        base_time = datetime.now() + timedelta(days=base_delay_days)

        # Get engagement patterns
        patterns = self.engagement_patterns.get(prospect_id, [])

        if not patterns:
            # Default: Tuesday-Thursday, 9-11 AM
            return self._adjust_to_business_hours(base_time)

        # Find most common engagement hour
        engagement_hours = [dt.hour for dt in patterns]
        if engagement_hours:
            optimal_hour = max(set(engagement_hours), key=engagement_hours.count)
            base_time = base_time.replace(hour=optimal_hour, minute=0)

        return self._adjust_to_business_hours(base_time)

    def _adjust_to_business_hours(self, dt: datetime) -> datetime:
        """Adjust to business hours (9 AM - 5 PM, Mon-Fri)"""

        # Move to next weekday if weekend
        while dt.weekday() >= 5:  # Saturday = 5, Sunday = 6
            dt += timedelta(days=1)

        # Adjust hour to business hours
        if dt.hour < 9:
            dt = dt.replace(hour=9, minute=0)
        elif dt.hour >= 17:
            dt = dt.replace(hour=9, minute=0)
            dt += timedelta(days=1)

        return dt

    def track_engagement(self, prospect_id: str, engagement_time: datetime):
        """Track when prospect engages (for pattern learning)"""
        self.engagement_patterns[prospect_id].append(engagement_time)

    def get_due_tasks(self) -> List[Dict]:
        """Get tasks that are due now"""

        now = datetime.now()

        due_tasks = [
            task for task in self.scheduled_tasks
            if task["scheduled_for"] <= now and task["status"] == "scheduled"
        ]

        # Sort by priority
        due_tasks.sort(key=lambda x: x["priority"], reverse=True)

        return due_tasks

    def mark_completed(self, task_id: str, success: bool):
        """Mark task as completed"""

        for task in self.scheduled_tasks:
            if task["task_id"] == task_id:
                task["status"] = "completed" if success else "failed"
                task["completed_at"] = datetime.now()

                # Schedule retry if failed
                if not success and task.get("retry_count", 0) < 3:
                    self._schedule_retry(task)

                break

    def _schedule_retry(self, failed_task: Dict):
        """Schedule automatic retry"""

        retry_count = failed_task.get("retry_count", 0) + 1

        # Exponential backoff: 1 day, 3 days, 7 days
        delay_days = 2 ** retry_count

        retry_task = {
            **failed_task,
            "task_id": f"retry_{failed_task['task_id']}_{retry_count}",
            "scheduled_for": datetime.now() + timedelta(days=delay_days),
            "retry_count": retry_count,
            "status": "scheduled",
            "original_task_id": failed_task["task_id"]
        }

        self.scheduled_tasks.append(retry_task)
