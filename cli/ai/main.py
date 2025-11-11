#!/usr/bin/env python3
"""
🚀 SuperClaude AI CLI - Interface en ligne de commande unifiée

Usage:
    ai run <intent> [options]
    ai <team>:<agent> [options]
    ai status
    ai metrics
    ai list

Examples:
    ai run watch.collect --ecosystems github pypi npm --since 7d
    ai run pr.linter --pr 128 --max-comments 10 --format md
    ai run security.audit --diff HEAD~1 --blocking --budget 0.5
    ai adk:watch_collect --since 7d
    ai anthropic:doc_hunter --query "Claude API documentation"
    ai status
    ai metrics
    ai list

Version: 1.0.0
"""

import sys
import os
import json
import argparse
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Ajout du répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.contracts import TaskMessage, TaskResult, TaskConstraints, PolicyMode
from core.ai_core import AICore
from core.super_claude import SuperClaude, AgentTeam, AgentTask


class AICLI:
    """
    🖥️ Interface CLI pour SuperClaude Multi-Agents
    """

    def __init__(self):
        self.ai_core = AICore()
        self.super_claude = SuperClaude()
        self.ai_dir = Path(".ai")

    def print_banner(self):
        """Affiche la bannière du CLI"""
        print("""
╔═══════════════════════════════════════════════════════════╗
║         🧠 SuperClaude Multi-Agents CLI v1.0            ║
║    Orchestration intelligente d'agents IA spécialisés     ║
╚═══════════════════════════════════════════════════════════╝
""")

    def cmd_run(self, args: argparse.Namespace) -> int:
        """
        Exécute une tâche via un intent

        Args:
            args: Arguments parsés (intent, options)

        Returns:
            Code de sortie (0 = succès, 1 = erreur)
        """
        intent = args.intent

        # Construction des inputs depuis les arguments
        inputs = {}

        # Options communes
        if hasattr(args, 'ecosystems') and args.ecosystems:
            inputs['ecosystems'] = args.ecosystems
        if hasattr(args, 'since') and args.since:
            inputs['since'] = args.since
        if hasattr(args, 'pr') and args.pr:
            inputs['pr'] = args.pr
        if hasattr(args, 'diff') and args.diff:
            inputs['diff'] = args.diff
        if hasattr(args, 'query') and args.query:
            inputs['query'] = args.query
        if hasattr(args, 'repo') and args.repo:
            inputs['repo'] = args.repo
        if hasattr(args, 'path') and args.path:
            inputs['path'] = args.path

        # Construction des contraintes
        policy = PolicyMode.BLOCKING if args.blocking else PolicyMode.ADVISORY
        constraints = TaskConstraints(
            budget_usd=args.budget,
            latency_s=args.latency,
            policy=policy
        )

        # Création du TaskMessage
        task = TaskMessage(
            intent=intent,
            inputs=inputs,
            constraints=constraints
        )

        print(f"🎯 Exécution de la tâche: {intent}")
        print(f"   Budget: ${constraints.budget_usd} | Latency: {constraints.latency_s}s | Policy: {policy.value}")

        # Soumission de la tâche
        success = self.ai_core.submit_task(task, priority=args.priority)

        if not success:
            print("❌ Échec de la soumission de la tâche")
            return 1

        # Routage vers le bon agent
        agent = self.ai_core.route_task(task)
        if not agent:
            print("❌ Aucun agent disponible pour cet intent")
            return 1

        print(f"✓ Agent sélectionné: {agent.team}/{agent.agent_name}")

        # Exécution via SuperClaude
        if args.dry_run:
            print(f"\n🔍 Mode DRY-RUN - Tâche non exécutée")
            print(f"\nTaskMessage:")
            print(task.to_json())
            return 0

        # Exécution réelle
        try:
            result = asyncio.run(self._execute_task(agent.team, agent.agent_name, inputs))

            # Conversion en TaskResult
            task_result = self._convert_to_task_result(task.task_id, result, agent)

            # Enregistrement du résultat
            self.ai_core.record_result(task_result)

            # Affichage du résultat
            print(f"\n✅ Tâche complétée: {task_result.status.value}")
            print(f"   Score: {task_result.score}/100")
            print(f"   Coût: ${task_result.metrics.cost_usd:.4f}")
            print(f"   Latency: {task_result.metrics.latency_ms}ms")

            if task_result.artefacts:
                print(f"\n📦 Artefacts générés:")
                for artefact in task_result.artefacts:
                    print(f"   - {artefact}")

            # Format de sortie
            if args.format == "json":
                print(f"\n{task_result.to_json()}")
            elif args.format == "md":
                print(f"\n{self._format_markdown(task_result)}")

            return 0 if task_result.is_success() else 1

        except Exception as e:
            print(f"❌ Erreur d'exécution: {str(e)}")
            return 1

    async def _execute_task(
        self,
        team: str,
        agent_name: str,
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Exécute une tâche via SuperClaude"""
        team_enum = AgentTeam(team)

        if team_enum == AgentTeam.ADK:
            return await self.super_claude.delegate_to_adk(agent_name, inputs)
        elif team_enum == AgentTeam.ANTHROPIC:
            return await self.super_claude.delegate_to_anthropic(agent_name, inputs)
        elif team_enum == AgentTeam.OPENAI:
            return await self.super_claude.delegate_to_openai(agent_name, inputs)
        else:
            raise ValueError(f"Unknown team: {team}")

    def _convert_to_task_result(
        self,
        task_id: str,
        raw_result: Dict[str, Any],
        agent: Any
    ) -> TaskResult:
        """Convertit un résultat brut en TaskResult"""
        from core.contracts import TaskStatus, TaskResult, TaskCost

        # Extraction du statut
        status_str = raw_result.get("status", "error")
        if status_str == "success":
            status = TaskStatus.OK
        elif status_str == "error":
            status = TaskStatus.ERROR
        else:
            status = TaskStatus(status_str) if status_str in ["ok", "advisory", "blocking"] else TaskStatus.ERROR

        # Extraction des métriques
        tokens = raw_result.get("tokens_used", raw_result.get("tokens", {}))
        cost = TaskCost(
            cost_usd=raw_result.get("cost_usd", 0.0),
            latency_ms=raw_result.get("latency_ms", 0),
            tokens=tokens
        )

        # Construction du TaskResult
        return TaskResult(
            task_id=task_id,
            status=status,
            score=raw_result.get("score", 85),  # Score par défaut
            artefacts=raw_result.get("artefacts", []),
            sources=raw_result.get("sources", []),
            model=f"{agent.team}:{agent.agent_name}",
            error=raw_result.get("error", ""),
            metrics=cost,
            result_data=raw_result.get("result", {})
        )

    def _format_markdown(self, result: TaskResult) -> str:
        """Formate un résultat en Markdown"""
        md = f"""# Résultat de tâche: {result.task_id}

## Statut: {result.status.value.upper()}

**Score**: {result.score}/100
**Modèle**: {result.model}
**Coût**: ${result.metrics.cost_usd:.4f}
**Latence**: {result.metrics.latency_ms}ms

## Artefacts

"""
        for artefact in result.artefacts:
            md += f"- `{artefact}`\n"

        if result.sources:
            md += "\n## Sources\n\n"
            for source in result.sources:
                md += f"- {source}\n"

        if result.error:
            md += f"\n## Erreur\n\n```\n{result.error}\n```\n"

        return md

    def cmd_status(self, args: argparse.Namespace) -> int:
        """Affiche le statut du système"""
        print("📊 SuperClaude Status")
        print("=" * 50)

        metrics = self.ai_core.get_metrics()

        print(f"\n📋 Queue:")
        print(f"   Tâches en attente: {metrics['queue_size']}")

        print(f"\n💰 Budget:")
        print(f"   Dépensé aujourd'hui: ${metrics['budget_spent_today']:.2f}")
        print(f"   Restant: ${metrics['budget_remaining']:.2f}")
        print(f"   Tâches aujourd'hui: {metrics['tasks_today']}")

        print(f"\n📈 Métriques:")
        for key, value in metrics.items():
            if key not in ['queue_size', 'budget_spent_today', 'budget_remaining', 'tasks_today']:
                print(f"   {key}: {value}")

        return 0

    def cmd_metrics(self, args: argparse.Namespace) -> int:
        """Affiche les métriques détaillées"""
        metrics = self.ai_core.get_metrics()

        if args.format == "json":
            print(json.dumps(metrics, indent=2))
        else:
            print("📊 Métriques SuperClaude")
            print("=" * 50)
            print(json.dumps(metrics, indent=2))

        return 0

    def cmd_list(self, args: argparse.Namespace) -> int:
        """Liste les agents disponibles"""
        print("📋 Agents disponibles")
        print("=" * 50)

        agents = self.super_claude.get_available_agents()

        for team, agent_list in agents.items():
            print(f"\n🔹 Équipe {team.upper()}")
            for agent in agent_list:
                print(f"   - {agent}")

        # Mapping des intents
        print("\n\n🎯 Intents supportés")
        print("=" * 50)

        intent_map = {}
        for agent in self.ai_core.registry.agents:
            for intent in agent.intents:
                if intent not in intent_map:
                    intent_map[intent] = []
                intent_map[intent].append(f"{agent.team}/{agent.agent_name}")

        for intent, agents in sorted(intent_map.items()):
            print(f"\n{intent}:")
            for agent in agents:
                print(f"   → {agent}")

        return 0

    def cmd_health(self, args: argparse.Namespace) -> int:
        """
        Health check pour monitoring et déploiement

        Vérifie:
        - AI Core fonctionnel
        - Bridges disponibles
        - Configuration valide
        - Système prêt à traiter des requêtes

        Returns:
            0 si healthy, 1 si degraded/unhealthy
        """
        try:
            status = "healthy"
            components = {}
            issues = []

            # Vérifier AI Core
            try:
                metrics = self.ai_core.get_metrics()
                components["ai_core"] = "ok"
            except Exception as e:
                components["ai_core"] = "error"
                issues.append(f"AI Core error: {str(e)}")
                status = "unhealthy"

            # Vérifier configuration Anthropic
            anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
            if anthropic_key and anthropic_key.startswith("sk-ant-"):
                components["anthropic_config"] = "ok"
            elif anthropic_key == "sk-ant-api03-..." or not anthropic_key:
                components["anthropic_config"] = "not_configured"
                issues.append("ANTHROPIC_API_KEY not configured")
                status = "degraded" if status == "healthy" else status
            else:
                components["anthropic_config"] = "invalid"
                issues.append("ANTHROPIC_API_KEY appears invalid")
                status = "degraded" if status == "healthy" else status

            # Vérifier configuration ADK
            adk_bridge = os.environ.get("ADK_BRIDGE_PATH")
            if adk_bridge and Path(adk_bridge).exists():
                components["adk_bridge"] = "ok"
            elif adk_bridge:
                components["adk_bridge"] = "missing"
                issues.append(f"ADK bridge not found: {adk_bridge}")
                status = "degraded" if status == "healthy" else status
            else:
                components["adk_bridge"] = "not_configured"

            # Vérifier répertoires essentiels
            if self.ai_dir.exists():
                components["data_dir"] = "ok"
            else:
                components["data_dir"] = "missing"
                issues.append(".ai directory missing")
                status = "degraded" if status == "healthy" else status

            # Construire le résultat
            health_status = {
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "components": components
            }

            if issues:
                health_status["issues"] = issues

            # Format de sortie
            if args.format == "json":
                print(json.dumps(health_status, indent=2))
            else:
                # Format texte coloré
                status_emoji = {
                    "healthy": "✅",
                    "degraded": "⚠️",
                    "unhealthy": "❌"
                }

                print(f"\n{status_emoji.get(status, '❓')} Health Status: {status.upper()}")
                print("=" * 50)
                print(f"Timestamp: {health_status['timestamp']}")
                print(f"Version: {health_status['version']}")

                print("\nComponents:")
                for component, state in components.items():
                    state_emoji = "✅" if state == "ok" else "⚠️" if state == "not_configured" else "❌"
                    print(f"  {state_emoji} {component}: {state}")

                if issues:
                    print("\nIssues:")
                    for issue in issues:
                        print(f"  ⚠️ {issue}")

            # Exit code selon le statut
            return 0 if status == "healthy" else 1

        except Exception as e:
            error_status = {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }

            if args.format == "json":
                print(json.dumps(error_status, indent=2))
            else:
                print(f"\n❌ Health Check Failed: {str(e)}")

            return 1


def main():
    """Point d'entrée principal du CLI"""
    parser = argparse.ArgumentParser(
        description="SuperClaude AI CLI - Orchestration multi-agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai run watch.collect --ecosystems github pypi --since 7d
  ai run pr.linter --pr 128 --format md
  ai run security.audit --diff HEAD~1 --blocking
  ai status
  ai metrics
  ai list
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commande à exécuter")

    # Commande: run
    run_parser = subparsers.add_parser("run", help="Exécuter une tâche via intent")
    run_parser.add_argument("intent", help="Intent de la tâche (ex: watch.collect)")
    run_parser.add_argument("--budget", type=float, default=0.75, help="Budget max en USD (défaut: 0.75)")
    run_parser.add_argument("--latency", type=int, default=60, help="Latence max en secondes (défaut: 60)")
    run_parser.add_argument("--blocking", action="store_true", help="Mode blocking (échec = arrêt)")
    run_parser.add_argument("--priority", type=int, default=1, help="Priorité de la tâche (défaut: 1)")
    run_parser.add_argument("--format", choices=["json", "md", "text"], default="text", help="Format de sortie")
    run_parser.add_argument("--dry-run", action="store_true", help="Simulation sans exécution")

    # Options spécifiques par intent
    run_parser.add_argument("--ecosystems", nargs="+", help="Écosystèmes à surveiller (watch.collect)")
    run_parser.add_argument("--since", help="Période de surveillance (ex: 7d)")
    run_parser.add_argument("--pr", type=int, help="Numéro de PR (pr.linter)")
    run_parser.add_argument("--diff", help="Diff à analyser (security.audit)")
    run_parser.add_argument("--query", help="Requête de recherche (doc.search)")
    run_parser.add_argument("--repo", help="Repository cible")
    run_parser.add_argument("--path", help="Chemin de fichier/dossier")

    # Commande: status
    subparsers.add_parser("status", help="Afficher le statut du système")

    # Commande: metrics
    metrics_parser = subparsers.add_parser("metrics", help="Afficher les métriques")
    metrics_parser.add_argument("--format", choices=["json", "text"], default="text", help="Format de sortie")

    # Commande: list
    subparsers.add_parser("list", help="Lister les agents disponibles")

    # Commande: health
    health_parser = subparsers.add_parser("health", help="Health check du système")
    health_parser.add_argument("--format", choices=["json", "text"], default="text", help="Format de sortie")

    args = parser.parse_args()

    # Création du CLI
    cli = AICLI()

    # Si aucune commande, afficher l'aide
    if not args.command:
        cli.print_banner()
        parser.print_help()
        return 0

    # Routage des commandes
    if args.command == "run":
        return cli.cmd_run(args)
    elif args.command == "status":
        return cli.cmd_status(args)
    elif args.command == "metrics":
        return cli.cmd_metrics(args)
    elif args.command == "list":
        return cli.cmd_list(args)
    elif args.command == "health":
        return cli.cmd_health(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
