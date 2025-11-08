#!/usr/bin/env python3
"""
🌉 OpenAI Bridge (Phase 3 Prototype)

Expose les agents OpenAI au protocole MCP/STDIO.
Les agents retournent actuellement des réponses factices afin de documenter
le contrat d'appel tout en attendant l'intégration réelle des API OpenAI.
"""

import json
import sys
from typing import Dict, Any

TOOLS: Dict[str, Dict[str, Any]] = {
    "ui_to_code": {
        "description": "Convertit une maquette (PNG/Figma) en composants UI annotés WCAG.",
        "schema": {
            "type": "object",
            "properties": {
                "mockup_path": {"type": "string", "description": "Chemin/URL de la maquette"},
                "framework": {"type": "string", "description": "Stack cible (react, vue, flutter)", "default": "react"},
                "accessibility": {"type": "boolean", "description": "Inclure les notes WCAG", "default": True}
            },
            "required": ["mockup_path"]
        }
    },
    "migrator_5000": {
        "description": "Prépare un plan de migration complexe (framework/SDK).",
        "schema": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Répertoire à analyser"},
                "target": {"type": "string", "description": "Cible de migration (ex: django4)"},
                "constraints": {"type": "string", "description": "Notes ou exigences"}
            },
            "required": ["repo", "target"]
        }
    },
    "creative_studio": {
        "description": "Génère des contenus créatifs multi-canal (email/social/visuel).",
        "schema": {
            "type": "object",
            "properties": {
                "brief": {"type": "string", "description": "Brief marketing"},
                "channels": {"type": "array", "items": {"type": "string"}, "description": "Canaux ciblés"},
                "tone": {"type": "string", "description": "Ton (playful, serious, etc.)", "default": "playful"}
            },
            "required": ["brief"]
        }
    }
}


def _rpc_result(content: Dict[str, Any], req_id: Any) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "content": [{"type": "text", "text": json.dumps(content)}]
        }
    }


def dispatch(tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if tool not in TOOLS:
        return {
            "status": "error",
            "error": f"openai tool '{tool}' inconnu",
            "result": None
        }

    return {
        "status": "not_implemented",
        "message": "Agents OpenAI en phase prototype. Implémentez l'appel OpenAI SDK avant activation.",
        "result": {
            "echo": params,
            "agent": tool,
            "next_steps": [
                "Activer OPENAI_AGENTS_ENABLED=true",
                "Renseigner OPENAI_API_KEY",
                "Brancher les appels OpenAI dans agents/openai/bridge.py"
            ]
        }
    }


def dispatch_rpc(request: Dict[str, Any]) -> Dict[str, Any]:
    method = request.get("method")

    if method == "initialize":
        return _rpc_result({
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "openai-bridge-prototype",
                "version": "0.1.0",
                "description": "Bridge OpenAI Phase 3 (stub)"
            }
        }, request.get("id"))

    if method == "tools/list":
        tools = []
        for name, meta in TOOLS.items():
            tools.append({
                "name": name,
                "description": meta["description"],
                "inputSchema": meta["schema"]
            })
        return _rpc_result({"tools": tools}, request.get("id"))

    if method == "tools/call":
        params = request.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})
        result = dispatch(name, arguments)
        return _rpc_result(result, request.get("id"))

    return {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "error": {"code": -32601, "message": f"Unknown method {method}"}
    }


def main() -> None:
    # Mode CLI direct: python bridge.py <tool> '{"param": "value"}'
    if len(sys.argv) >= 2 and sys.argv[1] != "-":
        tool_name = sys.argv[1]
        params_json = sys.argv[2] if len(sys.argv) > 2 else "{}"
        try:
            params = json.loads(params_json)
        except json.JSONDecodeError as exc:
            print(json.dumps({"status": "error", "error": f"JSON invalide: {exc}"}), flush=True)
            return
        print(json.dumps(dispatch(tool_name, params)), flush=True)
        return

    # Mode STDIO / MCP
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            print(json.dumps({"status": "error", "error": f"JSON invalide: {exc}"}), flush=True)
            continue

        if "method" in payload:
            response = dispatch_rpc(payload)
        else:
            tool = payload.get("tool")
            params = payload.get("params", {})
            response = dispatch(tool, params)

        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
