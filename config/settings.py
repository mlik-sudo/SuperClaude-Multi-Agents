#!/usr/bin/env python3
"""
⚙️ Configuration Super Claude Multi-Agents

Gestion centralisée des paramètres et chemins des bridges
"""

import os
from pathlib import Path
from typing import Optional

BOOL_TRUE = {"1", "true", "yes", "on"}


def _str_to_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in BOOL_TRUE

# Racine du projet
PROJECT_ROOT = Path(__file__).parent.parent

def get_anthropic_bridge_path() -> str:
    """
    🔍 Résolution du chemin du bridge Anthropic

    Ordre de priorité :
    1. Variable d'environnement ANTHROPIC_BRIDGE_PATH
    2. Chemin par défaut : agents/anthropic/bridge.py

    Returns:
        Chemin absolu du bridge

    Raises:
        FileNotFoundError: Si le bridge n'existe pas
        ValueError: Si le chemin est invalide
    """
    # Tentative via variable d'environnement
    env_path = os.environ.get("ANTHROPIC_BRIDGE_PATH")
    if env_path:
        path = Path(env_path)
        if not path.is_absolute():
            path = PROJECT_ROOT / path

        if not path.exists():
            raise FileNotFoundError(
                f"Bridge Anthropic introuvable via ANTHROPIC_BRIDGE_PATH: {path}\n"
                f"Vérifiez la variable d'environnement."
            )

        if not path.is_file():
            raise ValueError(
                f"ANTHROPIC_BRIDGE_PATH pointe vers un répertoire, pas un fichier: {path}"
            )

        return str(path)

    # Fallback vers chemin par défaut
    default_path = PROJECT_ROOT / "agents" / "anthropic" / "bridge.py"

    if not default_path.exists():
        raise FileNotFoundError(
            f"Bridge Anthropic introuvable au chemin par défaut: {default_path}\n"
            f"Assurez-vous que le fichier existe ou définissez ANTHROPIC_BRIDGE_PATH."
        )

    return str(default_path)


def get_adk_bridge_path() -> str:
    """
    🔍 Résolution du chemin du bridge ADK

    Returns:
        Chemin absolu du bridge ADK

    Raises:
        FileNotFoundError: Si le bridge n'existe pas
    """
    env_path = os.environ.get("ADK_BRIDGE_PATH")
    if env_path:
        path = Path(env_path)
        if not path.is_absolute():
            path = PROJECT_ROOT / path

        if not path.exists():
            raise FileNotFoundError(f"Bridge ADK introuvable: {path}")

        return str(path)

    # Fallback
    default_path = PROJECT_ROOT / "agents" / "adk" / "bridge.py"
    if not default_path.exists():
        raise FileNotFoundError(f"Bridge ADK introuvable: {default_path}")

    return str(default_path)


def get_openai_bridge_path(strict: bool = False) -> Optional[str]:
    """
    🔍 Résolution du chemin du bridge OpenAI (Phase 3)

    Returns:
        Chemin absolu du bridge ou None si non implémenté
    """
    env_path = os.environ.get("OPENAI_BRIDGE_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return str(path)

    default_path = PROJECT_ROOT / "agents" / "openai" / "bridge.py"
    if default_path.exists():
        return str(default_path)

    if strict:
        raise FileNotFoundError(
            "Bridge OpenAI introuvable : définissez OPENAI_BRIDGE_PATH ou créez agents/openai/bridge.py"
        )

    return None


# Feature flags
OPENAI_AGENTS_ENABLED = _str_to_bool(os.environ.get("OPENAI_AGENTS_ENABLED"), False)

# Configuration MCP
MCP_SERVER_CONFIG = PROJECT_ROOT / "mcp" / "servers.json"

# Configuration des modèles
ANTHROPIC_DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
OPENAI_DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4")

# Timeouts (secondes)
BRIDGE_TIMEOUT = int(os.environ.get("BRIDGE_TIMEOUT", "60"))
AGENT_TIMEOUT = int(os.environ.get("AGENT_TIMEOUT", "120"))

# Logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


if __name__ == "__main__":
    # Tests de configuration
    print("🧪 Test de configuration Super Claude")
    print(f"📁 Racine projet: {PROJECT_ROOT}")

    try:
        print(f"✅ Bridge ADK: {get_adk_bridge_path()}")
    except FileNotFoundError as e:
        print(f"❌ Bridge ADK: {e}")

    try:
        print(f"✅ Bridge Anthropic: {get_anthropic_bridge_path()}")
    except FileNotFoundError as e:
        print(f"❌ Bridge Anthropic: {e}")

    openai_path = get_openai_bridge_path()
    if openai_path:
        print(f"✅ Bridge OpenAI: {openai_path}")
    else:
        status = "Désactivé" if not OPENAI_AGENTS_ENABLED else "Non implémenté (Phase 3)"
        print(f"⏳ Bridge OpenAI: {status}")

    print(f"\n⚙️ Configuration:")
    print(f"  - Modèle Anthropic: {ANTHROPIC_DEFAULT_MODEL}")
    print(f"  - Modèle OpenAI: {OPENAI_DEFAULT_MODEL}")
    print(f"  - Agents OpenAI activés: {OPENAI_AGENTS_ENABLED}")
    print(f"  - Timeout bridge: {BRIDGE_TIMEOUT}s")
    print(f"  - Timeout agent: {AGENT_TIMEOUT}s")
