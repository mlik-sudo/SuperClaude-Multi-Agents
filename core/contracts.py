#!/usr/bin/env python3
"""
📋 Contrats A2A - Standardisation des messages inter-agents

Définit les structures de données pour la communication Agent-to-Agent (A2A)
conformément au protocole SuperClaude Multi-Agents.

Version: 1.0.0
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Literal
from enum import Enum
from datetime import datetime
import uuid
import json


class TaskStatus(Enum):
    """Statuts possibles d'une tâche"""
    OK = "ok"
    ADVISORY = "advisory"
    BLOCKING = "blocking"
    ERROR = "error"


class PolicyMode(Enum):
    """Modes de politique d'exécution"""
    BLOCKING = "blocking"      # Échec bloque le pipeline
    ADVISORY = "advisory"       # Échec ne bloque pas, juste un warning


@dataclass
class TaskConstraints:
    """
    Contraintes d'exécution d'une tâche

    Attributes:
        budget_usd: Budget maximum en USD pour cette tâche
        latency_s: Latence maximale acceptée en secondes
        policy: Mode de politique (blocking ou advisory)
    """
    budget_usd: float = 0.75
    latency_s: int = 60
    policy: PolicyMode = PolicyMode.ADVISORY

    def to_dict(self) -> Dict[str, Any]:
        return {
            "budget_usd": self.budget_usd,
            "latency_s": self.latency_s,
            "policy": self.policy.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskConstraints':
        policy = PolicyMode(data.get("policy", "advisory"))
        return cls(
            budget_usd=data.get("budget_usd", 0.75),
            latency_s=data.get("latency_s", 60),
            policy=policy
        )


@dataclass
class TaskContext:
    """
    Contexte d'exécution d'une tâche

    Attributes:
        memory_keys: Clés de mémoire à charger (pour RAG)
        attachments: Fichiers ou données attachés
        metadata: Métadonnées additionnelles
    """
    memory_keys: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskContext':
        return cls(
            memory_keys=data.get("memory_keys", []),
            attachments=data.get("attachments", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class TaskMessage:
    """
    📨 Contrat de message A2A (requête)

    Message envoyé par l'orchestrateur vers un agent pour exécuter une tâche.

    Attributes:
        task_id: Identifiant unique de la tâche
        intent: Intent de la tâche (ex: "watch.collect", "security.audit")
        inputs: Paramètres d'entrée spécifiques à l'agent
        constraints: Contraintes d'exécution (budget, latence, policy)
        context: Contexte additionnel (mémoire, attachments)

    Example:
        >>> msg = TaskMessage(
        ...     intent="watch.collect",
        ...     inputs={"repo": ".", "ecosystems": ["github", "pypi"]},
        ...     constraints=TaskConstraints(budget_usd=0.5, latency_s=30)
        ... )
    """
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    intent: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    constraints: TaskConstraints = field(default_factory=TaskConstraints)
    context: TaskContext = field(default_factory=TaskContext)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        """Conversion vers dictionnaire pour sérialisation JSON"""
        return {
            "task_id": self.task_id,
            "intent": self.intent,
            "inputs": self.inputs,
            "constraints": self.constraints.to_dict(),
            "context": self.context.to_dict(),
            "timestamp": self.timestamp
        }

    def to_json(self) -> str:
        """Sérialisation JSON"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskMessage':
        """Création depuis un dictionnaire"""
        return cls(
            task_id=data.get("task_id", str(uuid.uuid4())),
            intent=data.get("intent", ""),
            inputs=data.get("inputs", {}),
            constraints=TaskConstraints.from_dict(data.get("constraints", {})),
            context=TaskContext.from_dict(data.get("context", {})),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat() + "Z")
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'TaskMessage':
        """Désérialisation JSON"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class TaskCost:
    """
    💰 Métriques de coût d'exécution

    Attributes:
        cost_usd: Coût en USD
        latency_ms: Latence en millisecondes
        tokens: Consommation de tokens (si applicable)
    """
    cost_usd: float = 0.0
    latency_ms: int = 0
    tokens: Dict[str, int] = field(default_factory=dict)  # {"input": N, "output": M, "total": T}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TaskResult:
    """
    📤 Contrat de résultat A2A (réponse)

    Résultat retourné par un agent après exécution d'une tâche.

    Attributes:
        task_id: Identifiant de la tâche (référence au TaskMessage)
        status: Statut d'exécution (ok, advisory, blocking, error)
        score: Score de confiance/qualité (0-100)
        artefacts: Liste des artefacts générés (chemins relatifs à .ai/)
        sources: Sources de données utilisées
        model: Modèle IA utilisé (format: "provider:model@version")
        decision_log: Chemin vers le log détaillé de décision
        error: Message d'erreur (si status == error)
        metrics: Métriques d'exécution (coût, latence, tokens)
        result_data: Données de résultat (flexibles selon l'agent)

    Example:
        >>> result = TaskResult(
        ...     task_id="abc-123",
        ...     status=TaskStatus.OK,
        ...     score=95,
        ...     artefacts=["watch.ndjson", "sources.json"],
        ...     sources=["github:owner/repo@commit"],
        ...     model="gemini:1.5-flash@2024-11"
        ... )
    """
    task_id: str = ""
    status: TaskStatus = TaskStatus.OK
    score: int = 0  # 0-100
    artefacts: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    model: str = ""  # Format: "provider:model@version"
    decision_log: str = ""  # Chemin relatif: .ai/logs/<task_id>.ndjson
    error: str = ""
    metrics: TaskCost = field(default_factory=TaskCost)
    result_data: Dict[str, Any] = field(default_factory=dict)  # Données spécifiques à l'agent
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        """Conversion vers dictionnaire pour sérialisation JSON"""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "score": self.score,
            "artefacts": self.artefacts,
            "sources": self.sources,
            "model": self.model,
            "decision_log": self.decision_log,
            "error": self.error,
            "cost_usd": self.metrics.cost_usd,
            "latency_ms": self.metrics.latency_ms,
            "tokens": self.metrics.tokens,
            "result_data": self.result_data,
            "timestamp": self.timestamp
        }

    def to_json(self) -> str:
        """Sérialisation JSON"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskResult':
        """Création depuis un dictionnaire"""
        status = TaskStatus(data.get("status", "ok"))
        metrics = TaskCost(
            cost_usd=data.get("cost_usd", 0.0),
            latency_ms=data.get("latency_ms", 0),
            tokens=data.get("tokens", {})
        )
        return cls(
            task_id=data.get("task_id", ""),
            status=status,
            score=data.get("score", 0),
            artefacts=data.get("artefacts", []),
            sources=data.get("sources", []),
            model=data.get("model", ""),
            decision_log=data.get("decision_log", ""),
            error=data.get("error", ""),
            metrics=metrics,
            result_data=data.get("result_data", {}),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat() + "Z")
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'TaskResult':
        """Désérialisation JSON"""
        return cls.from_dict(json.loads(json_str))

    def is_success(self) -> bool:
        """Vérifie si le résultat est un succès"""
        return self.status in [TaskStatus.OK, TaskStatus.ADVISORY]

    def is_blocking(self) -> bool:
        """Vérifie si le résultat est bloquant"""
        return self.status == TaskStatus.BLOCKING


# Utilitaires de validation

def validate_intent(intent: str) -> bool:
    """
    Valide le format d'un intent

    Format attendu: "<team>.<action>" ou "<category>.<action>"
    Exemples: "watch.collect", "security.audit", "pr.linter"
    """
    parts = intent.split(".")
    return len(parts) == 2 and all(part.isidentifier() for part in parts)


def validate_source(source: str) -> bool:
    """
    Valide le format d'une source

    Formats attendus:
    - github:owner/repo@commit
    - pypi:package@version
    - npm:package@version
    - gemini:model@version
    - claude:model@version
    - openai:model@version
    - mcp:server/tool
    - file:path/to/file:line
    """
    if ":" not in source:
        return False

    provider, rest = source.split(":", 1)
    valid_providers = ["github", "pypi", "npm", "gemini", "claude", "openai", "mcp", "file", "sonarqube"]

    return provider in valid_providers and len(rest) > 0


# Exemples d'utilisation

if __name__ == "__main__":
    # Exemple de création d'un TaskMessage
    print("📨 Exemple TaskMessage:")
    print("-" * 50)

    msg = TaskMessage(
        intent="watch.collect",
        inputs={
            "repo": ".",
            "ecosystems": ["github", "pypi", "npm"],
            "since": "7d"
        },
        constraints=TaskConstraints(
            budget_usd=0.5,
            latency_s=30,
            policy=PolicyMode.ADVISORY
        ),
        context=TaskContext(
            memory_keys=["project:superclaude", "last_runs:watch"],
            attachments=[]
        )
    )

    print(msg.to_json())
    print()

    # Exemple de création d'un TaskResult
    print("📤 Exemple TaskResult:")
    print("-" * 50)

    result = TaskResult(
        task_id=msg.task_id,
        status=TaskStatus.OK,
        score=95,
        artefacts=["artefacts/watch/watch.ndjson", "artefacts/watch/sources.json"],
        sources=[
            "github:mlik-sudo/SuperClaude-Multi-Agents@main",
            "pypi:anthropic@latest",
            "npm:typescript@latest"
        ],
        model="gemini:1.5-flash@2024-11",
        decision_log=f"logs/{msg.task_id}.ndjson",
        metrics=TaskCost(
            cost_usd=0.12,
            latency_ms=4180,
            tokens={"input": 1200, "output": 800, "total": 2000}
        ),
        result_data={
            "total_items": 15,
            "new_items": 8,
            "ecosystems": {
                "github": 5,
                "pypi": 3,
                "npm": 0
            }
        }
    )

    print(result.to_json())
    print()

    # Validation
    print("✅ Validations:")
    print("-" * 50)
    print(f"Intent 'watch.collect' valide: {validate_intent('watch.collect')}")
    print(f"Intent 'invalid' valide: {validate_intent('invalid')}")
    print(f"Source 'github:mlik-sudo/repo@main' valide: {validate_source('github:mlik-sudo/repo@main')}")
    print(f"Source 'invalid' valide: {validate_source('invalid')}")
