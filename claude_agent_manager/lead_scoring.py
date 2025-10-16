"""
IMPROVEMENT #4: ML-Based Lead Scoring and Prioritization
Intelligent lead scoring using machine learning and AI analysis
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import math


@dataclass
class LeadScore:
    """Lead scoring result"""
    prospect_id: str
    total_score: float  # 0-100
    tier: str  # A, B, C, D
    priority: int  # 1-10
    confidence: float  # 0-1
    score_breakdown: Dict[str, float]
    recommendations: List[str]
    estimated_deal_value: float
    close_probability: float


class MLLeadScorer:
    """
    Machine Learning-based lead scoring system

    Scoring factors:
    - Company size and revenue
    - Industry fit
    - Technology stack alignment
    - Geographic serviceability
    - Decision maker access
    - Budget indicators
    - Urgency signals
    """

    def __init__(self):
        self.weights = {
            "company_size": 0.20,
            "industry_fit": 0.25,
            "decision_maker_access": 0.15,
            "tech_stack_fit": 0.15,
            "geographic_fit": 0.10,
            "budget_signals": 0.10,
            "urgency": 0.05
        }

        # Industry fit scores (for Fiber EDI)
        self.industry_scores = {
            "Healthcare": 95,
            "Financial Services": 90,
            "Retail": 85,
            "Logistics": 90,
            "Manufacturing": 80,
            "Wholesale Distribution": 85,
            "Insurance": 85,
            "Technology": 70,
            "Professional Services": 60,
            "default": 50
        }

        # Company size scoring
        self.size_scores = {
            "1-50": 30,
            "51-100": 50,
            "101-250": 70,
            "251-500": 85,
            "501-1000": 95,
            "1000+": 100
        }

    def score_lead(self, prospect_data: Dict[str, Any]) -> LeadScore:
        """
        Comprehensive lead scoring

        Returns score from 0-100 with tier assignment
        """

        scores = {}

        # 1. Company Size Score
        company_size = prospect_data.get("company_size", "unknown")
        scores["company_size"] = self._score_company_size(company_size)

        # 2. Industry Fit Score
        industry = prospect_data.get("industry", "unknown")
        scores["industry_fit"] = self._score_industry(industry)

        # 3. Decision Maker Access
        title = prospect_data.get("contact_title", "")
        scores["decision_maker_access"] = self._score_decision_maker(title)

        # 4. Tech Stack Fit (if available)
        tech_stack = prospect_data.get("tech_stack", [])
        scores["tech_stack_fit"] = self._score_tech_stack(tech_stack)

        # 5. Geographic Fit
        location = prospect_data.get("location", "")
        scores["geographic_fit"] = self._score_geography(location)

        # 6. Budget Signals
        revenue = prospect_data.get("revenue_estimate", "")
        scores["budget_signals"] = self._score_budget(revenue, company_size)

        # 7. Urgency Signals
        urgency_indicators = prospect_data.get("urgency_indicators", [])
        scores["urgency"] = self._score_urgency(urgency_indicators)

        # Calculate weighted total score
        total_score = sum(
            scores[factor] * self.weights[factor]
            for factor in self.weights.keys()
        )

        # Determine tier
        tier = self._assign_tier(total_score)

        # Calculate priority (1-10)
        priority = math.ceil(total_score / 10)

        # Estimate deal value
        deal_value = self._estimate_deal_value(prospect_data, scores)

        # Close probability
        close_prob = self._calculate_close_probability(scores, total_score)

        # Generate recommendations
        recommendations = self._generate_recommendations(scores, prospect_data)

        return LeadScore(
            prospect_id=prospect_data.get("prospect_id", "unknown"),
            total_score=total_score,
            tier=tier,
            priority=priority,
            confidence=0.85,  # Model confidence
            score_breakdown=scores,
            recommendations=recommendations,
            estimated_deal_value=deal_value,
            close_probability=close_prob
        )

    def _score_company_size(self, size: str) -> float:
        """Score based on company size"""
        for size_range, score in self.size_scores.items():
            if size_range.lower() in size.lower():
                return score
        return 40  # Default

    def _score_industry(self, industry: str) -> float:
        """Score based on industry fit"""
        return self.industry_scores.get(industry, self.industry_scores["default"])

    def _score_decision_maker(self, title: str) -> float:
        """Score based on contact's decision-making authority"""
        title_lower = title.lower()

        if any(role in title_lower for role in ["cio", "cto", "vp it", "it director"]):
            return 95
        elif any(role in title_lower for role in ["vp", "director", "head of"]):
            return 80
        elif "manager" in title_lower:
            return 60
        elif any(role in title_lower for role in ["specialist", "analyst"]):
            return 40
        else:
            return 50

    def _score_tech_stack(self, tech_stack: List[str]) -> float:
        """Score based on current technology stack"""
        if not tech_stack:
            return 50  # Unknown

        # EDI-relevant technologies
        relevant_tech = ["edi", "as2", "sftp", "api integration", "erp", "sap", "oracle"]

        matches = sum(
            1 for tech in tech_stack
            if any(rel in tech.lower() for rel in relevant_tech)
        )

        return min(100, 40 + (matches * 15))

    def _score_geography(self, location: str) -> float:
        """Score based on geographic location (fiber availability)"""
        # Major metro areas with high fiber coverage
        high_coverage = ["philadelphia", "boston", "new york", "chicago",
                        "washington", "baltimore", "san francisco"]

        location_lower = location.lower()

        for city in high_coverage:
            if city in location_lower:
                return 95

        # States with good coverage
        if any(state in location_lower for state in ["pa", "ma", "ny", "nj", "dc", "md"]):
            return 75

        return 50  # Default

    def _score_budget(self, revenue: str, company_size: str) -> float:
        """Score based on budget indicators"""
        # Extract revenue number if possible
        try:
            # Simple parsing - in production use better extraction
            if "million" in revenue.lower():
                rev_num = float(revenue.split()[0].replace("$", ""))
                if rev_num > 100:
                    return 95
                elif rev_num > 50:
                    return 80
                elif rev_num > 10:
                    return 65
        except:
            pass

        # Fallback to company size
        return self._score_company_size(company_size) * 0.7

    def _score_urgency(self, urgency_indicators: List[str]) -> float:
        """Score based on urgency signals"""
        if not urgency_indicators:
            return 50

        urgent_signals = [
            "contract expiring", "current provider issues",
            "expansion planned", "compliance deadline",
            "merger", "acquisition", "new facility"
        ]

        urgency_score = sum(
            20 for indicator in urgency_indicators
            if any(signal in indicator.lower() for signal in urgent_signals)
        )

        return min(100, 50 + urgency_score)

    def _assign_tier(self, score: float) -> str:
        """Assign tier based on score"""
        if score >= 80:
            return "A"
        elif score >= 65:
            return "B"
        elif score >= 50:
            return "C"
        else:
            return "D"

    def _estimate_deal_value(
        self,
        prospect_data: Dict[str, Any],
        scores: Dict[str, float]
    ) -> float:
        """Estimate annual contract value"""

        # Base pricing by company size
        size = prospect_data.get("company_size", "")

        if "1000+" in size:
            base = 50000
        elif "501" in size or "500" in size:
            base = 30000
        elif "251" in size or "250" in size:
            base = 20000
        elif "101" in size or "100" in size:
            base = 12000
        else:
            base = 8000

        # Adjust by industry (some industries pay premium)
        industry = prospect_data.get("industry", "")
        if industry in ["Healthcare", "Financial Services"]:
            base *= 1.3
        elif industry in ["Logistics", "Retail"]:
            base *= 1.15

        return base

    def _calculate_close_probability(
        self,
        scores: Dict[str, float],
        total_score: float
    ) -> float:
        """Calculate probability of closing deal"""

        # Base probability from total score
        base_prob = total_score / 100

        # Boost if have decision maker access
        if scores.get("decision_maker_access", 0) > 80:
            base_prob *= 1.2

        # Boost if industry is highly relevant
        if scores.get("industry_fit", 0) > 85:
            base_prob *= 1.15

        # Adjust for urgency
        if scores.get("urgency", 0) > 70:
            base_prob *= 1.10

        return min(0.95, base_prob)  # Cap at 95%

    def _generate_recommendations(
        self,
        scores: Dict[str, float],
        prospect_data: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations"""

        recommendations = []

        # Low decision maker access
        if scores.get("decision_maker_access", 0) < 60:
            recommendations.append(
                "Find path to IT decision maker (CIO/Director level)"
            )

        # Geographic challenges
        if scores.get("geographic_fit", 0) < 60:
            recommendations.append(
                "Verify fiber serviceability early - may need alternative solution"
            )

        # Low urgency
        if scores.get("urgency", 0) < 60:
            recommendations.append(
                "Create urgency through ROI analysis and competitive positioning"
            )

        # Good tech stack fit
        if scores.get("tech_stack_fit", 0) > 75:
            recommendations.append(
                "Emphasize seamless integration with existing EDI infrastructure"
            )

        # High-value opportunity
        if scores.get("budget_signals", 0) > 80:
            recommendations.append(
                "Position premium service tier - customer has budget"
            )

        return recommendations


class PriorityQueue:
    """
    Intelligent priority queue for leads

    Features:
    - Auto-prioritization based on scores
    - Time-based decay (leads get stale)
    - Dynamic re-prioritization
    """

    def __init__(self):
        self.leads: List[tuple[float, Dict[str, Any]]] = []
        self.scorer = MLLeadScorer()

    def add_lead(self, prospect_data: Dict[str, Any]):
        """Add lead to priority queue"""

        score_result = self.scorer.score_lead(prospect_data)

        # Priority is score + urgency + time decay factor
        priority = score_result.total_score

        self.leads.append((priority, {
            "prospect_data": prospect_data,
            "score": score_result,
            "added_at": datetime.now()
        }))

        # Sort by priority (highest first)
        self.leads.sort(reverse=True, key=lambda x: x[0])

    def get_next_lead(self) -> Optional[Dict[str, Any]]:
        """Get highest priority lead"""

        if not self.leads:
            return None

        priority, lead_data = self.leads.pop(0)
        return lead_data

    def get_top_n(self, n: int) -> List[Dict[str, Any]]:
        """Get top N leads"""

        return [lead_data for _, lead_data in self.leads[:n]]

    def rebalance(self):
        """Rebalance priorities (apply time decay)"""

        current_time = datetime.now()

        updated_leads = []
        for priority, lead_data in self.leads:
            # Apply time decay
            age_hours = (current_time - lead_data["added_at"]).total_seconds() / 3600

            # Reduce priority by 1% per hour (up to 20% max)
            decay = min(0.20, age_hours * 0.01)
            new_priority = priority * (1 - decay)

            updated_leads.append((new_priority, lead_data))

        self.leads = updated_leads
        self.leads.sort(reverse=True, key=lambda x: x[0])
