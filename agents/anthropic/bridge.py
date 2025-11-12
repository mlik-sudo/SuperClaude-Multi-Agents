#!/usr/bin/env python3
"""
🌉 Anthropic Bridge - Serveur MCP JSON-RPC STDIO

Passerelle entre Super Claude et l'équipe Anthropic via le SDK officiel.
Expose 3 agents spécialisés :
- research_agent : Recherche et synthèse d'informations
- code_agent : Génération et analyse de code
- writing_agent : Rédaction et édition de contenu
"""

import sys
import json
import os
from typing import Dict, Any, List
from anthropic import Anthropic

class AnthropicBridge:
    """
    🌉 Bridge MCP pour l'équipe Anthropic

    Communication via STDIO JSON-RPC avec le SDK Anthropic officiel
    """

    def __init__(self):
        self.client = None
        self.model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

        # Initialisation du client si API key présente
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            self.client = Anthropic(api_key=api_key)

        self.tools = {
            "research_agent": self.research_agent,
            "code_agent": self.code_agent,
            "writing_agent": self.writing_agent
        }

    def research_agent(self, query: str, depth: str = "standard") -> Dict[str, Any]:
        """
        🔍 Agent de recherche et synthèse

        Args:
            query: Question ou sujet de recherche
            depth: Profondeur ("quick", "standard", "deep")

        Returns:
            Synthèse structurée avec sources
        """
        # Validation des entrées
        if not query or not isinstance(query, str):
            return {
                "status": "error",
                "error": "Query doit être une chaîne non vide",
                "result": None
            }

        if len(query) > 10000:
            return {
                "status": "error",
                "error": f"Query trop longue: {len(query)} caractères (max 10000)",
                "result": None
            }

        if depth not in ["quick", "standard", "deep"]:
            return {
                "status": "error",
                "error": f"Depth invalide: {depth}. Valeurs acceptées: quick, standard, deep",
                "result": None
            }

        # Sanitization
        query = query.strip()

        if not self.client:
            return {
                "status": "error",
                "error": "ANTHROPIC_API_KEY non configurée",
                "result": None
            }

        system_prompt = """Tu es un agent de recherche expert.
Analyse la question et fournis une synthèse structurée avec :
- Résumé exécutif
- Points clés (bullet points)
- Insights et recommandations
Format: JSON avec {summary, key_points[], insights[], recommendations[]}"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048 if depth == "quick" else 4096 if depth == "standard" else 8192,
                system=system_prompt,
                messages=[{"role": "user", "content": query}]
            )

            # Extraction du texte de la réponse
            text_content = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    text_content += block.text

            return {
                "status": "success",
                "result": text_content,
                "tokens_used": {
                    "input": message.usage.input_tokens,
                    "output": message.usage.output_tokens,
                    "total": message.usage.input_tokens + message.usage.output_tokens
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "result": None
            }

    def code_agent(self, task: str, language: str = "python", context: str = "") -> Dict[str, Any]:
        """
        💻 Agent de génération et analyse de code

        Args:
            task: Tâche de code (génération, analyse, refactoring)
            language: Langage cible
            context: Contexte additionnel (code existant, contraintes)

        Returns:
            Code généré avec explications
        """
        # Validation des entrées
        if not task or not isinstance(task, str):
            return {
                "status": "error",
                "error": "Task doit être une chaîne non vide",
                "result": None
            }

        if len(task) > 5000:
            return {
                "status": "error",
                "error": f"Task trop longue: {len(task)} caractères (max 5000)",
                "result": None
            }

        if not isinstance(language, str) or len(language) > 50:
            return {
                "status": "error",
                "error": "Language doit être une chaîne valide (max 50 caractères)",
                "result": None
            }

        if context and len(context) > 20000:
            return {
                "status": "error",
                "error": f"Context trop long: {len(context)} caractères (max 20000)",
                "result": None
            }

        # Sanitization
        task = task.strip()
        language = language.strip()
        if context:
            context = context.strip()

        if not self.client:
            return {
                "status": "error",
                "error": "ANTHROPIC_API_KEY non configurée",
                "result": None
            }

        system_prompt = f"""Tu es un expert en développement {language}.
Génère du code propre, bien documenté et testé.
Format de réponse JSON :
{{
  "code": "code généré",
  "explanation": "explication des choix",
  "tests": "tests unitaires",
  "notes": ["notes importantes"]
}}"""

        user_content = f"Tâche: {task}"
        if context:
            user_content += f"\n\nContexte:\n{context}"

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_content}]
            )

            # Extraction du texte
            text_content = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    text_content += block.text

            return {
                "status": "success",
                "result": text_content,
                "tokens_used": {
                    "input": message.usage.input_tokens,
                    "output": message.usage.output_tokens,
                    "total": message.usage.input_tokens + message.usage.output_tokens
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "result": None
            }

    def writing_agent(self, content: str, style: str = "professional", task: str = "improve") -> Dict[str, Any]:
        """
        ✍️ Agent de rédaction et édition

        Args:
            content: Contenu à traiter
            style: Style cible ("professional", "casual", "technical", "marketing")
            task: Type de tâche ("improve", "summarize", "expand", "translate")

        Returns:
            Contenu rédigé/édité avec métadonnées
        """
        # Validation des entrées
        if not content or not isinstance(content, str):
            return {
                "status": "error",
                "error": "Content doit être une chaîne non vide",
                "result": None
            }

        if len(content) > 15000:
            return {
                "status": "error",
                "error": f"Content trop long: {len(content)} caractères (max 15000)",
                "result": None
            }

        valid_styles = ["professional", "casual", "technical", "marketing"]
        if style not in valid_styles:
            return {
                "status": "error",
                "error": f"Style invalide: {style}. Valeurs acceptées: {', '.join(valid_styles)}",
                "result": None
            }

        valid_tasks = ["improve", "summarize", "expand", "translate"]
        if task not in valid_tasks:
            return {
                "status": "error",
                "error": f"Task invalide: {task}. Valeurs acceptées: {', '.join(valid_tasks)}",
                "result": None
            }

        # Sanitization
        content = content.strip()

        if not self.client:
            return {
                "status": "error",
                "error": "ANTHROPIC_API_KEY non configurée",
                "result": None
            }

        task_prompts = {
            "improve": "Améliore ce contenu en gardant l'essence du message",
            "summarize": "Crée un résumé concis et percutant",
            "expand": "Développe ce contenu avec plus de détails et exemples",
            "translate": "Traduis ce contenu en gardant le ton et le style"
        }

        system_prompt = f"""Tu es un rédacteur expert en style {style}.
{task_prompts.get(task, "Traite ce contenu")}
Format JSON : {{"result": "contenu traité", "metadata": {{"word_count": N, "tone": "...", "changes": ["..."]}}}}"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": content}]
            )

            # Extraction du texte
            text_content = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    text_content += block.text

            return {
                "status": "success",
                "result": text_content,
                "tokens_used": {
                    "input": message.usage.input_tokens,
                    "output": message.usage.output_tokens,
                    "total": message.usage.input_tokens + message.usage.output_tokens
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "result": None
            }

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        📨 Traitement d'une requête JSON-RPC
        """
        if request.get("method") != "tools/call":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Méthode non supportée: {request.get('method')}"
                }
            }

        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in self.tools:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32602,
                    "message": f"Outil inconnu: {tool_name}. Disponibles: {list(self.tools.keys())}"
                }
            }

        # Exécution de l'outil
        result = self.tools[tool_name](**arguments)

        # Format MCP standard
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False)
                    }
                ]
            }
        }

    def run(self) -> None:
        """
        🚀 Boucle principale STDIO
        """
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = self.handle_request(request)
                print(json.dumps(response, ensure_ascii=False), flush=True)
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    bridge = AnthropicBridge()
    bridge.run()
