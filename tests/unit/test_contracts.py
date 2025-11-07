#!/usr/bin/env python3
"""
Tests unitaires pour les contrats A2A

Tests:
- Sérialisation/désérialisation TaskMessage
- Sérialisation/désérialisation TaskResult
- Validation des intents
- Validation des sources
"""

import sys
from pathlib import Path

# Ajout du répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import unittest
import json
from core.contracts import (
    TaskMessage,
    TaskResult,
    TaskConstraints,
    TaskContext,
    TaskCost,
    TaskStatus,
    PolicyMode,
    validate_intent,
    validate_source
)


class TestTaskMessage(unittest.TestCase):
    """Tests pour TaskMessage"""

    def test_task_message_creation(self):
        """Test création d'un TaskMessage"""
        msg = TaskMessage(
            intent="watch.collect",
            inputs={"repo": ".", "since": "7d"},
            constraints=TaskConstraints(budget_usd=0.5, latency_s=30)
        )

        self.assertEqual(msg.intent, "watch.collect")
        self.assertEqual(msg.inputs["repo"], ".")
        self.assertEqual(msg.constraints.budget_usd, 0.5)
        self.assertIsNotNone(msg.task_id)

    def test_task_message_serialization(self):
        """Test sérialisation JSON"""
        msg = TaskMessage(
            intent="watch.collect",
            inputs={"repo": "."}
        )

        # Sérialisation
        json_str = msg.to_json()
        data = json.loads(json_str)

        # Vérifications
        self.assertIn("task_id", data)
        self.assertEqual(data["intent"], "watch.collect")
        self.assertIn("constraints", data)

    def test_task_message_deserialization(self):
        """Test désérialisation JSON"""
        data = {
            "task_id": "test-123",
            "intent": "watch.collect",
            "inputs": {"repo": "."},
            "constraints": {"budget_usd": 0.75, "latency_s": 60, "policy": "advisory"},
            "context": {"memory_keys": [], "attachments": [], "metadata": {}}
        }

        msg = TaskMessage.from_dict(data)

        self.assertEqual(msg.task_id, "test-123")
        self.assertEqual(msg.intent, "watch.collect")
        self.assertEqual(msg.constraints.budget_usd, 0.75)

    def test_task_constraints(self):
        """Test TaskConstraints"""
        constraints = TaskConstraints(
            budget_usd=1.0,
            latency_s=120,
            policy=PolicyMode.BLOCKING
        )

        self.assertEqual(constraints.budget_usd, 1.0)
        self.assertEqual(constraints.latency_s, 120)
        self.assertEqual(constraints.policy, PolicyMode.BLOCKING)

        # Conversion dict
        data = constraints.to_dict()
        self.assertEqual(data["policy"], "blocking")


class TestTaskResult(unittest.TestCase):
    """Tests pour TaskResult"""

    def test_task_result_creation(self):
        """Test création d'un TaskResult"""
        result = TaskResult(
            task_id="test-123",
            status=TaskStatus.OK,
            score=95,
            artefacts=["test.md"],
            sources=["github:owner/repo@main"],
            model="gemini:1.5-flash@2024-11"
        )

        self.assertEqual(result.task_id, "test-123")
        self.assertEqual(result.status, TaskStatus.OK)
        self.assertEqual(result.score, 95)
        self.assertTrue(result.is_success())
        self.assertFalse(result.is_blocking())

    def test_task_result_with_metrics(self):
        """Test TaskResult avec métriques"""
        cost = TaskCost(
            cost_usd=0.12,
            latency_ms=4500,
            tokens={"input": 1200, "output": 800, "total": 2000}
        )

        result = TaskResult(
            task_id="test-123",
            status=TaskStatus.OK,
            metrics=cost
        )

        self.assertEqual(result.metrics.cost_usd, 0.12)
        self.assertEqual(result.metrics.latency_ms, 4500)
        self.assertEqual(result.metrics.tokens["total"], 2000)

    def test_task_result_serialization(self):
        """Test sérialisation JSON"""
        result = TaskResult(
            task_id="test-123",
            status=TaskStatus.OK,
            score=90,
            artefacts=["report.md"],
            sources=["github:test/repo@main"]
        )

        json_str = result.to_json()
        data = json.loads(json_str)

        self.assertEqual(data["task_id"], "test-123")
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["score"], 90)

    def test_task_result_statuses(self):
        """Test différents statuts"""
        # OK
        result_ok = TaskResult(status=TaskStatus.OK)
        self.assertTrue(result_ok.is_success())
        self.assertFalse(result_ok.is_blocking())

        # ADVISORY
        result_advisory = TaskResult(status=TaskStatus.ADVISORY)
        self.assertTrue(result_advisory.is_success())
        self.assertFalse(result_advisory.is_blocking())

        # BLOCKING
        result_blocking = TaskResult(status=TaskStatus.BLOCKING)
        self.assertFalse(result_blocking.is_success())
        self.assertTrue(result_blocking.is_blocking())

        # ERROR
        result_error = TaskResult(status=TaskStatus.ERROR, error="Test error")
        self.assertFalse(result_error.is_success())
        self.assertEqual(result_error.error, "Test error")


class TestValidation(unittest.TestCase):
    """Tests pour les fonctions de validation"""

    def test_validate_intent(self):
        """Test validation des intents"""
        # Valides
        self.assertTrue(validate_intent("watch.collect"))
        self.assertTrue(validate_intent("pr.review"))
        self.assertTrue(validate_intent("security.audit"))
        self.assertTrue(validate_intent("code.generate"))

        # Invalides
        self.assertFalse(validate_intent("invalid"))
        self.assertFalse(validate_intent("too.many.parts"))
        self.assertFalse(validate_intent(""))
        self.assertFalse(validate_intent("no-dots"))

    def test_validate_source(self):
        """Test validation des sources"""
        # Valides
        self.assertTrue(validate_source("github:owner/repo@main"))
        self.assertTrue(validate_source("pypi:package@1.0.0"))
        self.assertTrue(validate_source("npm:package@latest"))
        self.assertTrue(validate_source("gemini:1.5-flash@2024-11"))
        self.assertTrue(validate_source("claude:3.5-sonnet@latest"))
        self.assertTrue(validate_source("openai:gpt-4o@latest"))
        self.assertTrue(validate_source("mcp:server/tool"))
        self.assertTrue(validate_source("file:/path/to/file:123"))

        # Invalides
        self.assertFalse(validate_source("invalid"))
        self.assertFalse(validate_source(""))
        self.assertFalse(validate_source("unknown:source"))


class TestRoundTrip(unittest.TestCase):
    """Tests de round-trip (sérialisation + désérialisation)"""

    def test_task_message_round_trip(self):
        """Test round-trip TaskMessage"""
        original = TaskMessage(
            intent="watch.collect",
            inputs={"repo": ".", "since": "7d"},
            constraints=TaskConstraints(
                budget_usd=0.5,
                latency_s=30,
                policy=PolicyMode.BLOCKING
            ),
            context=TaskContext(
                memory_keys=["project:test"],
                attachments=["file.txt"],
                metadata={"key": "value"}
            )
        )

        # Sérialisation -> Désérialisation
        json_str = original.to_json()
        restored = TaskMessage.from_json(json_str)

        # Vérifications
        self.assertEqual(restored.task_id, original.task_id)
        self.assertEqual(restored.intent, original.intent)
        self.assertEqual(restored.inputs, original.inputs)
        self.assertEqual(restored.constraints.budget_usd, original.constraints.budget_usd)
        self.assertEqual(restored.context.memory_keys, original.context.memory_keys)

    def test_task_result_round_trip(self):
        """Test round-trip TaskResult"""
        original = TaskResult(
            task_id="test-123",
            status=TaskStatus.OK,
            score=95,
            artefacts=["test.md", "data.json"],
            sources=["github:owner/repo@main"],
            model="gemini:1.5-flash@2024-11",
            metrics=TaskCost(
                cost_usd=0.12,
                latency_ms=4500,
                tokens={"input": 1200, "output": 800, "total": 2000}
            ),
            result_data={"items": 15, "new": 8}
        )

        # Sérialisation -> Désérialisation
        json_str = original.to_json()
        restored = TaskResult.from_json(json_str)

        # Vérifications
        self.assertEqual(restored.task_id, original.task_id)
        self.assertEqual(restored.status, original.status)
        self.assertEqual(restored.score, original.score)
        self.assertEqual(restored.artefacts, original.artefacts)
        self.assertEqual(restored.sources, original.sources)
        self.assertEqual(restored.metrics.cost_usd, original.metrics.cost_usd)
        self.assertEqual(restored.result_data, original.result_data)


if __name__ == "__main__":
    unittest.main()
