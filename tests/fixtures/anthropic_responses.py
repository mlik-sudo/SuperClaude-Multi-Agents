"""
🧪 Fixtures de test pour les réponses Anthropic

Mocks réalistes des réponses des agents Anthropic pour les tests unitaires et d'intégration.
"""

import json
from typing import Dict, Any

# ===================================
# Research Agent Responses
# ===================================

RESEARCH_AGENT_SUCCESS = {
    "status": "success",
    "result": json.dumps({
        "summary": "Python reste le langage le plus populaire pour l'IA en 2024",
        "key_points": [
            "PyTorch et TensorFlow dominent le deep learning",
            "JAX gagne en popularité pour la recherche",
            "Hugging Face transforme l'accès aux modèles pré-entraînés"
        ],
        "insights": [
            "L'écosystème Python pour l'IA est mature et bien documenté",
            "Les outils de MLOps s'intègrent naturellement avec Python"
        ],
        "recommendations": [
            "Apprendre PyTorch pour le deep learning moderne",
            "Explorer Hugging Face pour les modèles pré-entraînés",
            "Utiliser Weights & Biases pour le tracking d'expériences"
        ]
    }),
    "tokens_used": {
        "input": 150,
        "output": 320,
        "total": 470
    }
}

RESEARCH_AGENT_QUICK = {
    "status": "success",
    "result": json.dumps({
        "summary": "Résumé rapide de la question",
        "key_points": ["Point 1", "Point 2"],
        "insights": [],
        "recommendations": []
    }),
    "tokens_used": {
        "input": 80,
        "output": 120,
        "total": 200
    }
}

RESEARCH_AGENT_DEEP = {
    "status": "success",
    "result": json.dumps({
        "summary": "Analyse approfondie avec contexte historique et projections futures",
        "key_points": [
            "Point détaillé 1 avec données",
            "Point détaillé 2 avec sources",
            "Point détaillé 3 avec comparaisons"
        ],
        "insights": [
            "Insight profond 1 basé sur l'analyse",
            "Insight profond 2 avec implications"
        ],
        "recommendations": [
            "Recommandation actionnable 1",
            "Recommandation actionnable 2",
            "Recommandation actionnable 3"
        ]
    }),
    "tokens_used": {
        "input": 250,
        "output": 850,
        "total": 1100
    }
}

# ===================================
# Code Agent Responses
# ===================================

CODE_AGENT_SUCCESS = {
    "status": "success",
    "result": json.dumps({
        "code": """def fibonacci(n: int) -> int:
    \"\"\"
    Calcule le n-ième nombre de Fibonacci.

    Args:
        n: Position dans la séquence (0-indexé)

    Returns:
        Le n-ième nombre de Fibonacci

    Raises:
        ValueError: Si n est négatif
    \"\"\"
    if n < 0:
        raise ValueError("n doit être positif")
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b""",
        "explanation": "Implémentation itérative optimisée O(n) avec gestion d'erreurs et docstring complète.",
        "tests": """import pytest

def test_fibonacci_base_cases():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1

def test_fibonacci_sequence():
    assert fibonacci(5) == 5
    assert fibonacci(10) == 55

def test_fibonacci_error():
    with pytest.raises(ValueError):
        fibonacci(-1)""",
        "notes": [
            "Complexité temporelle: O(n)",
            "Complexité spatiale: O(1)",
            "Alternative: mémorisation pour appels répétés"
        ]
    }),
    "tokens_used": {
        "input": 120,
        "output": 450,
        "total": 570
    }
}

CODE_AGENT_REFACTOR = {
    "status": "success",
    "result": json.dumps({
        "code": """# Code refactoré avec patterns modernes
from dataclasses import dataclass
from typing import Protocol

@dataclass
class User:
    id: int
    name: str
    email: str

class UserRepository(Protocol):
    def get(self, user_id: int) -> User | None: ...""",
        "explanation": "Refactoring vers dataclasses et protocols pour better typing",
        "tests": "# Tests adaptés au nouveau code",
        "notes": ["Utilise Python 3.10+ features", "Type-safe avec mypy"]
    }),
    "tokens_used": {
        "input": 200,
        "output": 380,
        "total": 580
    }
}

# ===================================
# Writing Agent Responses
# ===================================

WRITING_AGENT_SUCCESS = {
    "status": "success",
    "result": json.dumps({
        "result": """Super Claude Multi-Agents: Une Architecture Innovante pour l'IA

Super Claude représente une approche novatrice de l'orchestration multi-agents, combinant les forces de plusieurs plateformes d'IA de pointe. Cette architecture hybride permet de tirer parti des spécialisations uniques de chaque écosystème tout en maintenant une interface unifiée et intuitive.

L'innovation clé réside dans le système de bridge JSON-RPC qui assure une communication transparente entre les différentes équipes d'agents, tout en préservant l'isolation et la sécurité de chaque composant.""",
        "metadata": {
            "word_count": 87,
            "tone": "professional",
            "changes": [
                "Restructuré l'introduction pour plus d'impact",
                "Ajouté des termes techniques précis",
                "Amélioré la fluidité entre paragraphes"
            ]
        }
    }),
    "tokens_used": {
        "input": 180,
        "output": 240,
        "total": 420
    }
}

WRITING_AGENT_SUMMARIZE = {
    "status": "success",
    "result": json.dumps({
        "result": "Super Claude est une plateforme d'orchestration multi-agents qui unifie ADK, Anthropic et OpenAI via des bridges JSON-RPC, offrant flexibilité et performance optimale.",
        "metadata": {
            "word_count": 23,
            "tone": "professional",
            "changes": ["Condensé en une phrase", "Gardé les points essentiels"]
        }
    }),
    "tokens_used": {
        "input": 350,
        "output": 80,
        "total": 430
    }
}

# ===================================
# Error Responses
# ===================================

ERROR_NO_API_KEY = {
    "status": "error",
    "error": "ANTHROPIC_API_KEY non configurée",
    "result": None
}

ERROR_INVALID_TOOL = {
    "jsonrpc": "2.0",
    "id": 1,
    "error": {
        "code": -32602,
        "message": "Outil inconnu: invalid_agent. Disponibles: ['research_agent', 'code_agent', 'writing_agent']"
    }
}

ERROR_TIMEOUT = {
    "status": "timeout",
    "output": "Bridge Anthropic timeout après 60s"
}

ERROR_JSON_PARSE = {
    "status": "error",
    "output": "Réponse JSON invalide du bridge: Expecting value: line 1 column 1 (char 0)"
}

# ===================================
# Helper Functions
# ===================================

def create_mcp_response(agent_result: Dict[str, Any], request_id: int = 1) -> Dict[str, Any]:
    """
    Crée une réponse MCP JSON-RPC standard.

    Args:
        agent_result: Résultat de l'agent (doit avoir status, result, tokens_used)
        request_id: ID de la requête JSON-RPC

    Returns:
        Réponse MCP formatée
    """
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(agent_result, ensure_ascii=False)
                }
            ]
        }
    }


def create_error_response(error_code: int, error_message: str, request_id: int = 1) -> Dict[str, Any]:
    """
    Crée une réponse d'erreur JSON-RPC.

    Args:
        error_code: Code d'erreur JSON-RPC
        error_message: Message d'erreur
        request_id: ID de la requête

    Returns:
        Réponse d'erreur formatée
    """
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": error_code,
            "message": error_message
        }
    }


# ===================================
# Test Scenarios
# ===================================

TEST_SCENARIOS = {
    "research_success": create_mcp_response(RESEARCH_AGENT_SUCCESS),
    "research_quick": create_mcp_response(RESEARCH_AGENT_QUICK),
    "research_deep": create_mcp_response(RESEARCH_AGENT_DEEP),
    "code_success": create_mcp_response(CODE_AGENT_SUCCESS),
    "code_refactor": create_mcp_response(CODE_AGENT_REFACTOR),
    "writing_success": create_mcp_response(WRITING_AGENT_SUCCESS),
    "writing_summarize": create_mcp_response(WRITING_AGENT_SUMMARIZE),
    "error_no_api_key": create_mcp_response(ERROR_NO_API_KEY),
    "error_invalid_tool": ERROR_INVALID_TOOL,
}
