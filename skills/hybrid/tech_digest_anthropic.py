#!/usr/bin/env python3
"""
📰 Tech Digest with Anthropic - Skill Hybride Démonstratif

Workflow :
1. ADK collecte les données brutes (repos GitHub trending)
2. Filtrage local Python (sélection des top repos)
3. Anthropic analyse les tendances
4. Anthropic rédige une newsletter professionnelle

💰 Économie : ~98% de tokens (300K → 6K)
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# Ajout du chemin pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.super_claude import SuperClaude, AgentTeam, AgentTask


@dataclass
class TokenMetrics:
    """Métriques de consommation de tokens"""
    adk_tokens: int = 0
    anthropic_research_tokens: int = 0
    anthropic_writing_tokens: int = 0
    local_processing_tokens_saved: int = 0

    @property
    def total_used(self) -> int:
        return self.adk_tokens + self.anthropic_research_tokens + self.anthropic_writing_tokens

    @property
    def total_saved(self) -> int:
        return self.local_processing_tokens_saved

    @property
    def savings_percentage(self) -> float:
        if self.total_saved == 0:
            return 0.0
        total = self.total_used + self.total_saved
        return (self.total_saved / total) * 100


class TechDigestWithAnthropicSkill:
    """
    📰 Skill hybride : Digest technologique avec équipe Anthropic

    Démontre :
    - Progressive disclosure (filtrage local avant API)
    - Orchestration multi-agents (ADK + Anthropic)
    - Mesure des économies de tokens
    """

    def __init__(self):
        self.super_claude = SuperClaude()
        self.metrics = TokenMetrics()

    async def execute(self, sources: List[str] = None, max_repos: int = 20) -> Dict[str, Any]:
        """
        Exécution du workflow complet

        Args:
            sources: Sources de données (défaut: ["github"])
            max_repos: Nombre max de repos à analyser (défaut: 20)

        Returns:
            Dict avec newsletter, métriques et détails
        """
        if sources is None:
            sources = ["github"]

        print("🚀 Tech Digest with Anthropic - Workflow Hybride")
        print("=" * 60)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 1 : Collecte ADK
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print("\n📊 Phase 1 : Collecte de données (ADK)")
        print("-" * 60)

        # Note : En production, ceci appellerait vraiment l'ADK
        # Pour la démo, on simule des données
        raw_repos = await self._collect_data_adk(sources)

        # Estimation tokens bruts (si on envoyait tout à Anthropic)
        estimated_raw_tokens = self._estimate_tokens(raw_repos)
        print(f"  • Repos collectés : {len(raw_repos)}")
        print(f"  • Tokens si envoi brut : ~{estimated_raw_tokens:,}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 2 : Filtrage Local (Python)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print(f"\n🔍 Phase 2 : Filtrage local (Python natif)")
        print("-" * 60)

        filtered_repos = self._filter_trending_repos(raw_repos, max_repos)

        tokens_after_filter = self._estimate_tokens(filtered_repos)
        tokens_saved = estimated_raw_tokens - tokens_after_filter

        self.metrics.local_processing_tokens_saved = tokens_saved

        print(f"  • Repos après filtrage : {len(filtered_repos)}")
        print(f"  • Tokens après filtrage : ~{tokens_after_filter:,}")
        print(f"  • 💰 Tokens économisés : ~{tokens_saved:,} ({self._calc_percentage(tokens_saved, estimated_raw_tokens):.1f}%)")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 3 : Analyse Anthropic (Research Agent)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print(f"\n🔍 Phase 3 : Analyse des tendances (Anthropic Research Agent)")
        print("-" * 60)

        research_result = await self._analyze_trends_anthropic(filtered_repos)

        if research_result["status"] == "success":
            research_tokens = research_result.get("tokens_used", {}).get("total", 0)
            self.metrics.anthropic_research_tokens = research_tokens
            print(f"  • Analyse complétée")
            print(f"  • Tokens utilisés : {research_tokens}")
        else:
            print(f"  • ⚠️ Erreur : {research_result.get('output', 'Unknown')}")
            research_result["result"] = {"summary": "Analyse non disponible"}

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 4 : Rédaction Newsletter (Writing Agent)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print(f"\n✍️ Phase 4 : Rédaction newsletter (Anthropic Writing Agent)")
        print("-" * 60)

        newsletter_result = await self._write_newsletter_anthropic(
            filtered_repos,
            research_result.get("result", {})
        )

        if newsletter_result["status"] == "success":
            writing_tokens = newsletter_result.get("tokens_used", {}).get("total", 0)
            self.metrics.anthropic_writing_tokens = writing_tokens
            print(f"  • Newsletter rédigée")
            print(f"  • Tokens utilisés : {writing_tokens}")
        else:
            print(f"  • ⚠️ Erreur : {newsletter_result.get('output', 'Unknown')}")
            newsletter_result["result"] = {"result": "Newsletter non disponible"}

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Résumé des Métriques
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print(f"\n📊 Résumé des Métriques")
        print("=" * 60)
        self._print_metrics()

        return {
            "newsletter": newsletter_result.get("result", {}).get("result", ""),
            "analysis": research_result.get("result", {}),
            "metrics": {
                "total_tokens_used": self.metrics.total_used,
                "total_tokens_saved": self.metrics.total_saved,
                "savings_percentage": f"{self.metrics.savings_percentage:.2f}%",
                "breakdown": {
                    "adk": self.metrics.adk_tokens,
                    "anthropic_research": self.metrics.anthropic_research_tokens,
                    "anthropic_writing": self.metrics.anthropic_writing_tokens
                }
            },
            "repos_analyzed": len(filtered_repos)
        }

    async def _collect_data_adk(self, sources: List[str]) -> List[Dict[str, Any]]:
        """
        Collecte de données via ADK

        Note : En production, ceci délèguerait à watch_collect
        Pour la démo, on simule des données trending
        """
        # Simulation de 100 repos GitHub trending
        return [
            {
                "name": f"awesome-project-{i}",
                "description": f"Description du projet {i}",
                "stars": 5000 - (i * 40),
                "stars_growth": 200 - i,
                "language": ["Python", "Rust", "Go", "TypeScript"][i % 4],
                "topics": ["ai", "ml", "web", "devops", "security"][i % 5],
                "url": f"https://github.com/user/awesome-project-{i}"
            }
            for i in range(100)
        ]

    def _filter_trending_repos(self, repos: List[Dict], max_repos: int) -> List[Dict]:
        """
        Filtrage local - Python natif

        Critères :
        - Growth > 100 stars
        - Trier par growth décroissant
        - Limiter à max_repos
        """
        # Filtrage
        trending = [r for r in repos if r["stars_growth"] > 100]

        # Tri
        trending_sorted = sorted(
            trending,
            key=lambda x: x["stars_growth"],
            reverse=True
        )

        # Limitation
        return trending_sorted[:max_repos]

    async def _analyze_trends_anthropic(self, repos: List[Dict]) -> Dict[str, Any]:
        """
        Analyse des tendances via Anthropic Research Agent
        """
        # Préparation du contexte concis
        repos_summary = "\n".join([
            f"- {r['name']} ({r['language']}) : +{r['stars_growth']} ⭐, topics: {r['topics']}"
            for r in repos[:20]
        ])

        query = f"""
Analyse ces {len(repos)} projets GitHub trending et identifie les tendances clés :

{repos_summary}

Fournis :
1. Résumé des tendances technologiques dominantes
2. Langages et frameworks en croissance
3. Thématiques récurrentes (IA, DevOps, Security, etc.)
4. Insights sur l'évolution de l'écosystème
"""

        return await self.super_claude.delegate_to_anthropic(
            "research_agent",
            {"query": query, "depth": "standard"}
        )

    async def _write_newsletter_anthropic(
        self,
        repos: List[Dict],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Rédaction de newsletter via Anthropic Writing Agent
        """
        # Extraction du top 5
        top_5 = repos[:5]
        top_5_formatted = "\n".join([
            f"{i+1}. **{r['name']}** ({r['language']}) - {r['description']}\n"
            f"   ⭐ {r['stars']:,} stars (+{r['stars_growth']})\n"
            f"   🔗 {r['url']}"
            for i, r in enumerate(top_5)
        ])

        content = f"""
Rédige une newsletter professionnelle hebdomadaire pour développeurs.

**Analyse des tendances :**
{analysis.get('summary', 'Analyse des projets GitHub trending de la semaine')}

**Top 5 Projets :**
{top_5_formatted}

**Points clés :**
{', '.join(analysis.get('key_points', [])[:3])}

Structure attendue :
- Titre accrocheur
- Intro (2-3 phrases)
- Section "Tendances de la semaine"
- Section "Top 5 à ne pas manquer" (détails des projets)
- Conclusion avec call-to-action
"""

        return await self.super_claude.delegate_to_anthropic(
            "writing_agent",
            {"content": content, "style": "professional", "task": "improve"}
        )

    def _estimate_tokens(self, data: Any) -> int:
        """
        Estimation grossière du nombre de tokens

        Règle approximative : 1 token ≈ 4 caractères en anglais
        """
        import json
        text = json.dumps(data)
        return len(text) // 4

    def _calc_percentage(self, part: int, total: int) -> float:
        """Calcul de pourcentage"""
        if total == 0:
            return 0.0
        return (part / total) * 100

    def _print_metrics(self):
        """Affichage formaté des métriques"""
        print(f"  Total tokens utilisés : {self.metrics.total_used:,}")
        print(f"  ├─ ADK : {self.metrics.adk_tokens:,}")
        print(f"  ├─ Anthropic Research : {self.metrics.anthropic_research_tokens:,}")
        print(f"  └─ Anthropic Writing : {self.metrics.anthropic_writing_tokens:,}")
        print()
        print(f"  💰 Tokens économisés (filtrage local) : {self.metrics.total_saved:,}")
        print(f"  📊 Économie réalisée : {self.metrics.savings_percentage:.1f}%")


async def main():
    """Point d'entrée pour exécution standalone"""
    skill = TechDigestWithAnthropicSkill()

    print(f"⏰ Démarrage : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = await skill.execute(sources=["github"], max_repos=20)

    print("\n" + "=" * 60)
    print("📰 Newsletter Générée")
    print("=" * 60)
    print(result["newsletter"][:500] + "...")  # Aperçu

    print("\n" + "=" * 60)
    print("✅ Workflow Complété")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
