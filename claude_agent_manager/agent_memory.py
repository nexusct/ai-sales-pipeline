"""
IMPROVEMENT #3: Agent Memory and Context Learning System
Agents learn from previous interactions and improve over time
"""

import json
import pickle
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict
import hashlib


@dataclass
class Interaction:
    """Recorded agent interaction"""
    interaction_id: str
    agent_name: str
    prompt: str
    response: str
    context: Dict[str, Any]
    success: bool
    feedback_score: Optional[float] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AgentMemory:
    """
    Persistent memory system for agents

    Features:
    - Stores successful interactions
    - Retrieves similar past cases
    - Learns from feedback
    - Improves prompts over time
    """

    def __init__(self, storage_path: str = "agent_memory.db"):
        self.storage_path = storage_path
        self.memory: Dict[str, List[Interaction]] = defaultdict(list)
        self.success_patterns: Dict[str, List[str]] = defaultdict(list)
        self.load()

    def store_interaction(
        self,
        agent_name: str,
        prompt: str,
        response: str,
        context: Dict[str, Any],
        success: bool,
        feedback_score: Optional[float] = None
    ):
        """Store an interaction in memory"""

        interaction_id = self._generate_id(prompt, agent_name)

        interaction = Interaction(
            interaction_id=interaction_id,
            agent_name=agent_name,
            prompt=prompt,
            response=response,
            context=context,
            success=success,
            feedback_score=feedback_score
        )

        self.memory[agent_name].append(interaction)

        # Track successful patterns
        if success and feedback_score and feedback_score > 0.7:
            self.success_patterns[agent_name].append(prompt)

        # Persist
        self.save()

    def retrieve_similar(
        self,
        agent_name: str,
        prompt: str,
        limit: int = 5
    ) -> List[Interaction]:
        """Retrieve similar past interactions"""

        if agent_name not in self.memory:
            return []

        # Simple similarity: keyword overlap
        # In production, use embeddings/vector search
        prompt_keywords = set(prompt.lower().split())

        scored_interactions = []
        for interaction in self.memory[agent_name]:
            interaction_keywords = set(interaction.prompt.lower().split())
            similarity = len(prompt_keywords & interaction_keywords) / len(prompt_keywords | interaction_keywords)

            scored_interactions.append((similarity, interaction))

        # Sort by similarity, then success
        scored_interactions.sort(
            key=lambda x: (x[0], x[1].success, x[1].feedback_score or 0),
            reverse=True
        )

        return [interaction for _, interaction in scored_interactions[:limit]]

    def get_best_practices(self, agent_name: str) -> List[str]:
        """Get proven successful approaches for an agent"""

        if agent_name not in self.memory:
            return []

        # Find interactions with high success rates
        successful = [
            i for i in self.memory[agent_name]
            if i.success and (i.feedback_score or 0) > 0.7
        ]

        # Extract common patterns
        # In production: use NLP to extract key phrases
        return [i.prompt for i in successful[-10:]]  # Last 10 successes

    def get_statistics(self, agent_name: str) -> Dict[str, Any]:
        """Get agent performance statistics"""

        if agent_name not in self.memory:
            return {"total_interactions": 0}

        interactions = self.memory[agent_name]
        successes = [i for i in interactions if i.success]
        with_feedback = [i for i in interactions if i.feedback_score is not None]

        stats = {
            "total_interactions": len(interactions),
            "successful_interactions": len(successes),
            "success_rate": len(successes) / len(interactions) if interactions else 0,
            "average_feedback_score": sum(i.feedback_score for i in with_feedback) / len(with_feedback) if with_feedback else 0,
            "total_with_feedback": len(with_feedback)
        }

        return stats

    def enhance_prompt_with_memory(
        self,
        agent_name: str,
        base_prompt: str,
        context: Dict[str, Any]
    ) -> str:
        """Enhance prompt with relevant past learnings"""

        similar = self.retrieve_similar(agent_name, base_prompt, limit=3)

        if not similar:
            return base_prompt

        # Add context from similar successful cases
        enhancement = "\n\nRELEVANT PAST SUCCESSFUL APPROACHES:\n"

        for i, interaction in enumerate(similar, 1):
            if interaction.success:
                enhancement += f"\n{i}. Similar case: {interaction.prompt[:100]}..."
                enhancement += f"\n   Worked well: {interaction.response[:150]}...\n"

        return base_prompt + enhancement

    def _generate_id(self, prompt: str, agent_name: str) -> str:
        """Generate unique interaction ID"""
        content = f"{agent_name}:{prompt}:{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()

    def save(self):
        """Persist memory to disk"""
        try:
            with open(self.storage_path, 'wb') as f:
                # Convert to serializable format
                data = {
                    agent: [asdict(i) for i in interactions]
                    for agent, interactions in self.memory.items()
                }
                pickle.dump(data, f)
        except Exception as e:
            print(f"Warning: Could not save memory: {e}")

    def load(self):
        """Load memory from disk"""
        try:
            with open(self.storage_path, 'rb') as f:
                data = pickle.load(f)

                # Convert back to Interaction objects
                for agent, interactions in data.items():
                    self.memory[agent] = [
                        Interaction(**i) for i in interactions
                    ]
        except FileNotFoundError:
            pass  # New memory
        except Exception as e:
            print(f"Warning: Could not load memory: {e}")


class LearningAgent:
    """
    Enhanced agent that learns from experience

    Wraps base Claude agent with memory capabilities
    """

    def __init__(self, base_agent, memory: AgentMemory):
        self.base_agent = base_agent
        self.memory = memory

    async def process_task_with_learning(self, task):
        """Process task and learn from outcome"""

        # Enhance prompt with memory
        enhanced_prompt = self.memory.enhance_prompt_with_memory(
            agent_name=self.base_agent.config.name,
            base_prompt=task.prompt,
            context=task.context
        )

        # Create enhanced task
        enhanced_task = task
        enhanced_task.prompt = enhanced_prompt

        # Execute with base agent
        result = await self.base_agent.process_task(enhanced_task)

        # Store interaction
        self.memory.store_interaction(
            agent_name=self.base_agent.config.name,
            prompt=task.prompt,
            response=result.response if result.success else "",
            context=task.context,
            success=result.success,
            feedback_score=None  # Set later after evaluation
        )

        return result

    def provide_feedback(self, interaction_id: str, score: float):
        """Provide feedback on an interaction"""
        # Update interaction with feedback
        for interaction in self.memory.memory.get(self.base_agent.config.name, []):
            if interaction.interaction_id == interaction_id:
                interaction.feedback_score = score
                self.memory.save()
                break


class ContextRetentionSystem:
    """
    Maintains context across multiple interactions

    Features:
    - Conversation history
    - Cross-prospect insights
    - Industry learnings
    """

    def __init__(self):
        self.conversations: Dict[str, List[Dict]] = defaultdict(list)
        self.industry_insights: Dict[str, List[str]] = defaultdict(list)
        self.successful_approaches: Dict[str, Dict] = {}

    def add_to_conversation(
        self,
        conversation_id: str,
        role: str,
        message: str,
        metadata: Dict = None
    ):
        """Add message to conversation history"""

        self.conversations[conversation_id].append({
            "role": role,
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })

    def get_conversation_context(
        self,
        conversation_id: str,
        last_n: int = 10
    ) -> List[Dict]:
        """Get recent conversation history"""

        return self.conversations[conversation_id][-last_n:]

    def learn_industry_insight(self, industry: str, insight: str):
        """Store industry-specific learning"""

        self.industry_insights[industry].append({
            "insight": insight,
            "timestamp": datetime.now().isoformat()
        })

    def get_industry_context(self, industry: str) -> List[str]:
        """Get relevant industry insights"""

        return [
            i["insight"]
            for i in self.industry_insights.get(industry, [])[-5:]  # Last 5
        ]

    def record_successful_approach(
        self,
        approach_type: str,
        details: Dict[str, Any]
    ):
        """Record a successful approach for reuse"""

        approach_id = f"{approach_type}_{int(datetime.now().timestamp())}"

        self.successful_approaches[approach_id] = {
            "type": approach_type,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "use_count": 0
        }

    def get_proven_approach(self, approach_type: str) -> Optional[Dict]:
        """Get a proven approach of given type"""

        matches = [
            approach for approach in self.successful_approaches.values()
            if approach["type"] == approach_type
        ]

        if not matches:
            return None

        # Return most successful (most used)
        return max(matches, key=lambda x: x["use_count"])
