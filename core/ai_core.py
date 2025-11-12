#!/usr/bin/env python3
"""
🎯 AI Core - Orchestrateur Central Multi-Agents

Moteur central de SuperClaude gérant:
- Queue de tâches prioritaires
- Budgets et quotas
- Router de modèles/agents
- Observabilité et métriques
- Cache et optimisations

Version: 1.0.0
"""

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import heapq

from .contracts import (
    TaskMessage, TaskResult, TaskStatus, TaskConstraints, TaskCost,
    PolicyMode, validate_intent
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


# ========================================
# Utilitaires de Sécurité
# ========================================

def redact_sensitive_data(data: Any, redact_patterns: Optional[List[str]] = None) -> Any:
    """
    Masque les données sensibles dans les logs et les résultats.

    Args:
        data: Données à traiter (str, dict, list, ou autre)
        redact_patterns: Patterns regex additionnels à masquer

    Returns:
        Données avec les informations sensibles masquées

    Patterns masqués par défaut:
    - API keys (sk-*, api-*, key_*)
    - Tokens (Bearer, JWT)
    - Emails
    - Mots de passe
    - Secrets
    """
    # Patterns par défaut pour détecter les secrets
    default_patterns = [
        (r'sk-[a-zA-Z0-9-_]{20,}', 'sk-***REDACTED***'),  # API keys Anthropic/OpenAI
        (r'api-[a-zA-Z0-9-_]{20,}', 'api-***REDACTED***'),  # Generic API keys
        (r'key_[a-zA-Z0-9-_]{20,}', 'key_***REDACTED***'),  # Generic keys
        (r'Bearer\s+[a-zA-Z0-9\-._~+/]+=*', 'Bearer ***REDACTED***'),  # Bearer tokens
        (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '***EMAIL_REDACTED***'),  # Emails
        (r'"password"\s*:\s*"[^"]*"', '"password": "***REDACTED***"'),  # JSON passwords
        (r'"secret"\s*:\s*"[^"]*"', '"secret": "***REDACTED***"'),  # JSON secrets
        (r'"token"\s*:\s*"[^"]*"', '"token": "***REDACTED***"'),  # JSON tokens
    ]

    # Ajouter les patterns custom
    if redact_patterns:
        for pattern in redact_patterns:
            default_patterns.append((pattern, '***REDACTED***'))

    def _redact_string(text: str) -> str:
        """Masque les secrets dans une chaîne"""
        if not isinstance(text, str):
            return text

        redacted = text
        for pattern, replacement in default_patterns:
            redacted = re.sub(pattern, replacement, redacted)

        return redacted

    def _redact_recursive(obj: Any) -> Any:
        """Masque les secrets récursivement dans les structures"""
        if isinstance(obj, str):
            return _redact_string(obj)
        elif isinstance(obj, dict):
            return {k: _redact_recursive(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_redact_recursive(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(_redact_recursive(item) for item in obj)
        else:
            return obj

    return _redact_recursive(data)


@dataclass
class AgentCapability:
    """
    Capacité d'un agent

    Attributes:
        team: Équipe de l'agent (adk, anthropic, openai)
        agent_name: Nom de l'agent
        intents: Liste des intents supportés
        cost_per_token: Coût moyen par token (USD)
        avg_latency_ms: Latence moyenne (ms)
        sla_success_rate: Taux de succès SLA (0-100)
    """
    team: str
    agent_name: str
    intents: List[str]
    cost_per_token: float = 0.0
    avg_latency_ms: int = 1000
    sla_success_rate: float = 99.0


@dataclass
class BudgetTracker:
    """
    Suivi des budgets et quotas

    Attributes:
        daily_budget_usd: Budget journalier en USD
        per_task_budget_usd: Budget par tâche en USD
        spent_today_usd: Dépenses du jour en USD
        task_count_today: Nombre de tâches exécutées aujourd'hui
        last_reset: Date du dernier reset
    """
    daily_budget_usd: float = 10.0
    per_task_budget_usd: float = 0.75
    spent_today_usd: float = 0.0
    task_count_today: int = 0
    last_reset: datetime = field(default_factory=datetime.utcnow)

    def check_budget(self, required_usd: float) -> Tuple[bool, str]:
        """
        Vérifie si le budget est suffisant

        Returns:
            (authorized: bool, reason: str)
        """
        # Reset si nouveau jour
        now = datetime.utcnow()
        if now.date() > self.last_reset.date():
            self.spent_today_usd = 0.0
            self.task_count_today = 0
            self.last_reset = now

        # Vérification budget par tâche
        if required_usd > self.per_task_budget_usd:
            return False, f"Budget par tâche dépassé: {required_usd:.2f} > {self.per_task_budget_usd:.2f} USD"

        # Vérification budget journalier
        if self.spent_today_usd + required_usd > self.daily_budget_usd:
            remaining = self.daily_budget_usd - self.spent_today_usd
            return False, f"Budget journalier dépassé: reste {remaining:.2f} USD"

        return True, "OK"

    def record_spend(self, amount_usd: float):
        """Enregistre une dépense"""
        self.spent_today_usd += amount_usd
        self.task_count_today += 1


@dataclass
class PriorityTask:
    """
    Tâche avec priorité pour la queue

    Les tâches sont triées par:
    1. Priorité (plus haut = plus prioritaire)
    2. Timestamp (plus ancien = plus prioritaire)
    """
    priority: int
    timestamp: datetime
    task_message: TaskMessage
    callback: Optional[Any] = None

    def __lt__(self, other):
        # Inversion pour heapq (min-heap -> max-heap pour priorité)
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.timestamp < other.timestamp


class AgentRegistry:
    """
    🗂️ Registre des agents et leurs capacités

    Mappe les intents vers les agents selon:
    - Capacités fonctionnelles
    - Coût
    - Latence
    - SLA
    """

    def __init__(self):
        self.agents: List[AgentCapability] = []
        self.intent_map: Dict[str, List[AgentCapability]] = defaultdict(list)
        self._load_default_agents()

    def _load_default_agents(self):
        """Charge le catalogue d'agents par défaut"""

        # Équipe ADK (Google A2A)
        adk_agents = [
            AgentCapability(
                team="adk",
                agent_name="watch_collect",
                intents=["watch.collect"],
                cost_per_token=0.00001,  # Gemini Flash
                avg_latency_ms=5000,
                sla_success_rate=98.0
            ),
            AgentCapability(
                team="adk",
                agent_name="analyse_watch_report",
                intents=["watch.analyze"],
                cost_per_token=0.00001,
                avg_latency_ms=3000,
                sla_success_rate=99.0
            ),
            AgentCapability(
                team="adk",
                agent_name="curate_digest",
                intents=["curate.digest"],
                cost_per_token=0.00001,
                avg_latency_ms=4000,
                sla_success_rate=98.0
            ),
            AgentCapability(
                team="adk",
                agent_name="label_github_issue",
                intents=["github.label"],
                cost_per_token=0.00001,
                avg_latency_ms=2000,
                sla_success_rate=99.5
            ),
        ]

        # Équipe Anthropic (MCP)
        anthropic_agents = [
            AgentCapability(
                team="anthropic",
                agent_name="doc_hunter",
                intents=["doc.search", "research.doc"],
                cost_per_token=0.00003,  # Claude Sonnet
                avg_latency_ms=2500,
                sla_success_rate=99.5
            ),
            AgentCapability(
                team="anthropic",
                agent_name="test_architect",
                intents=["test.generate", "test.coverage"],
                cost_per_token=0.00003,
                avg_latency_ms=6000,
                sla_success_rate=97.0
            ),
            AgentCapability(
                team="anthropic",
                agent_name="refactor_master",
                intents=["code.refactor", "code.migrate"],
                cost_per_token=0.00003,
                avg_latency_ms=8000,
                sla_success_rate=96.0
            ),
            AgentCapability(
                team="anthropic",
                agent_name="pr_linter",
                intents=["pr.review", "pr.lint"],
                cost_per_token=0.00003,
                avg_latency_ms=3000,
                sla_success_rate=99.0
            ),
            AgentCapability(
                team="anthropic",
                agent_name="writing_studio",
                intents=["writing.docs", "writing.guide"],
                cost_per_token=0.00003,
                avg_latency_ms=4000,
                sla_success_rate=98.5
            ),
            # Anciens agents (compatibility)
            AgentCapability(
                team="anthropic",
                agent_name="research_agent",
                intents=["research.general"],
                cost_per_token=0.00003,
                avg_latency_ms=3000,
                sla_success_rate=99.0
            ),
            AgentCapability(
                team="anthropic",
                agent_name="code_agent",
                intents=["code.generate", "code.analyze"],
                cost_per_token=0.00003,
                avg_latency_ms=5000,
                sla_success_rate=97.5
            ),
            AgentCapability(
                team="anthropic",
                agent_name="writing_agent",
                intents=["writing.general"],
                cost_per_token=0.00003,
                avg_latency_ms=4000,
                sla_success_rate=98.0
            ),
        ]

        # Équipe OpenAI (Phase 3 - placeholder)
        openai_agents = [
            AgentCapability(
                team="openai",
                agent_name="ui_to_code",
                intents=["ui.convert", "vision.ui"],
                cost_per_token=0.00005,  # GPT-4o
                avg_latency_ms=7000,
                sla_success_rate=95.0
            ),
            AgentCapability(
                team="openai",
                agent_name="migrator_5000",
                intents=["code.migrate.complex"],
                cost_per_token=0.00005,
                avg_latency_ms=10000,
                sla_success_rate=94.0
            ),
            AgentCapability(
                team="openai",
                agent_name="creative_studio",
                intents=["creative.generate", "creative.variant"],
                cost_per_token=0.00005,
                avg_latency_ms=8000,
                sla_success_rate=96.0
            ),
        ]

        # Enregistrement
        all_agents = adk_agents + anthropic_agents + openai_agents
        for agent in all_agents:
            self.register_agent(agent)

    def register_agent(self, agent: AgentCapability):
        """Enregistre un agent et ses capacités"""
        self.agents.append(agent)
        for intent in agent.intents:
            self.intent_map[intent].append(agent)

        logger.info(f"Registered agent: {agent.team}/{agent.agent_name} with intents {agent.intents}")

    def find_best_agent(
        self,
        intent: str,
        constraints: TaskConstraints
    ) -> Optional[AgentCapability]:
        """
        Trouve le meilleur agent pour un intent donné

        Critères de sélection:
        1. Supporte l'intent
        2. Respecte les contraintes de budget et latence
        3. Meilleur SLA
        4. Coût le plus bas
        """
        if intent not in self.intent_map:
            logger.warning(f"No agent found for intent: {intent}")
            return None

        candidates = self.intent_map[intent]

        # Filtrage par contraintes
        filtered = [
            agent for agent in candidates
            if agent.avg_latency_ms <= constraints.latency_s * 1000
        ]

        if not filtered:
            logger.warning(f"No agent matches constraints for intent: {intent}")
            return None

        # Tri par SLA (desc) puis coût (asc)
        best = sorted(
            filtered,
            key=lambda a: (-a.sla_success_rate, a.cost_per_token)
        )[0]

        logger.info(f"Selected agent for '{intent}': {best.team}/{best.agent_name} (SLA: {best.sla_success_rate}%, cost: {best.cost_per_token})")

        return best


class TaskQueue:
    """
    📋 Queue de tâches avec priorité

    Gère l'ordonnancement des tâches selon leur priorité et timestamp
    """

    def __init__(self):
        self.heap: List[PriorityTask] = []
        self.pending_count = 0

    def enqueue(self, task: PriorityTask):
        """Ajoute une tâche à la queue"""
        heapq.heappush(self.heap, task)
        self.pending_count += 1
        logger.debug(f"Enqueued task {task.task_message.task_id} with priority {task.priority}")

    def dequeue(self) -> Optional[PriorityTask]:
        """Retire et retourne la tâche la plus prioritaire"""
        if not self.heap:
            return None

        task = heapq.heappop(self.heap)
        self.pending_count -= 1
        logger.debug(f"Dequeued task {task.task_message.task_id}")
        return task

    def is_empty(self) -> bool:
        """Vérifie si la queue est vide"""
        return len(self.heap) == 0

    def size(self) -> int:
        """Retourne la taille de la queue"""
        return len(self.heap)


class AICore:
    """
    🧠 AI Core - Orchestrateur Central

    Coordonne:
    - Registre d'agents
    - Queue de tâches
    - Budgets et quotas
    - Routage intelligent
    - Observabilité
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.registry = AgentRegistry()
        self.queue = TaskQueue()
        self.budget = BudgetTracker(
            daily_budget_usd=self.config.get("daily_budget_usd", 10.0),
            per_task_budget_usd=self.config.get("per_task_budget_usd", 0.75)
        )
        self.metrics = defaultdict(int)
        self.ai_dir = Path(".ai")
        self.ai_dir.mkdir(exist_ok=True)

    def _default_config(self) -> Dict[str, Any]:
        """Configuration par défaut"""
        return {
            "daily_budget_usd": 10.0,
            "per_task_budget_usd": 0.75,
            "max_concurrent_tasks": 5,
            "enable_cache": True,
            "enable_observability": True
        }

    def route_task(self, task_message: TaskMessage) -> Optional[AgentCapability]:
        """
        Route une tâche vers le meilleur agent

        Returns:
            Agent sélectionné ou None si aucun agent disponible
        """
        # Validation de l'intent
        if not validate_intent(task_message.intent):
            logger.error(f"Invalid intent format: {task_message.intent}")
            return None

        # Vérification du budget
        authorized, reason = self.budget.check_budget(task_message.constraints.budget_usd)
        if not authorized:
            logger.warning(f"Budget check failed: {reason}")
            if task_message.constraints.policy == PolicyMode.BLOCKING:
                return None

        # Sélection de l'agent
        agent = self.registry.find_best_agent(
            task_message.intent,
            task_message.constraints
        )

        return agent

    def submit_task(
        self,
        task_message: TaskMessage,
        priority: int = 1
    ) -> bool:
        """
        Soumet une tâche à la queue

        Args:
            task_message: Message de tâche
            priority: Priorité (plus haut = plus prioritaire)

        Returns:
            True si la tâche a été soumise avec succès
        """
        # Routage
        agent = self.route_task(task_message)
        if not agent:
            logger.error(f"No agent available for task {task_message.task_id}")
            return False

        # Ajout à la queue
        priority_task = PriorityTask(
            priority=priority,
            timestamp=datetime.utcnow(),
            task_message=task_message
        )

        self.queue.enqueue(priority_task)
        self.metrics["tasks_submitted"] += 1

        logger.info(f"Task {task_message.task_id} submitted to queue (intent: {task_message.intent})")

        return True

    def record_result(self, result: TaskResult):
        """
        Enregistre le résultat d'une tâche

        Met à jour:
        - Budgets
        - Métriques
        - Logs
        """
        # Mise à jour du budget
        self.budget.record_spend(result.metrics.cost_usd)

        # Métriques
        self.metrics["tasks_completed"] += 1
        self.metrics[f"tasks_{result.status.value}"] += 1
        self.metrics["total_cost_usd"] += result.metrics.cost_usd
        self.metrics["total_latency_ms"] += result.metrics.latency_ms

        # Logging dans USAGE.ndjson (avec redaction des secrets)
        usage_entry = {
            "timestamp": result.timestamp,
            "task_id": result.task_id,
            "status": result.status.value,
            "cost_usd": result.metrics.cost_usd,
            "latency_ms": result.metrics.latency_ms,
            "tokens": result.metrics.tokens,
            "model": result.model
        }

        # Redaction des données sensibles avant logging
        safe_usage_entry = redact_sensitive_data(usage_entry)

        usage_file = self.ai_dir / "USAGE.ndjson"
        with open(usage_file, "a") as f:
            f.write(json.dumps(safe_usage_entry) + "\n")

        logger.info(f"Recorded result for task {result.task_id}: {result.status.value} (cost: ${result.metrics.cost_usd:.4f}, latency: {result.metrics.latency_ms}ms)")

    def get_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques actuelles"""
        return {
            "queue_size": self.queue.size(),
            "budget_spent_today": self.budget.spent_today_usd,
            "budget_remaining": self.budget.daily_budget_usd - self.budget.spent_today_usd,
            "tasks_today": self.budget.task_count_today,
            **dict(self.metrics)
        }


# Exemple d'utilisation

if __name__ == "__main__":
    print("🧠 AI Core - Test d'orchestration")
    print("=" * 50)

    # Création de l'orchestrateur
    ai_core = AICore()

    # Création d'une tâche
    task = TaskMessage(
        intent="watch.collect",
        inputs={
            "ecosystems": ["github", "pypi"],
            "since": "7d"
        },
        constraints=TaskConstraints(
            budget_usd=0.5,
            latency_s=30
        )
    )

    # Soumission de la tâche
    success = ai_core.submit_task(task, priority=2)
    print(f"\nTâche soumise: {success}")

    # Affichage des métriques
    print(f"\nMétriques:")
    print(json.dumps(ai_core.get_metrics(), indent=2))

    # Simulation d'un résultat
    result = TaskResult(
        task_id=task.task_id,
        status=TaskStatus.OK,
        score=95,
        artefacts=["artefacts/watch/watch.ndjson"],
        sources=["github:mlik-sudo/SuperClaude@main"],
        model="gemini:1.5-flash@2024-11",
        metrics=TaskCost(cost_usd=0.12, latency_ms=4500, tokens={"total": 2000})
    )

    ai_core.record_result(result)

    # Métriques finales
    print(f"\nMétriques après exécution:")
    print(json.dumps(ai_core.get_metrics(), indent=2))
