"""Automated workflow and agent evaluation."""

import json
import uuid
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation_record import EvaluationType
from app.repositories.evaluation import EvaluationRepository


class WorkflowEvaluator:
    """Evaluates agent outputs and workflow correctness."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = EvaluationRepository(session)

    async def evaluate_workflow(
        self, workflow_id: uuid.UUID, state: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Run all evaluations on a completed workflow."""
        results = []

        results.append(await self._eval_json_validity(workflow_id, state))
        results.append(await self._eval_workflow_correctness(workflow_id, state))
        results.append(await self._eval_tool_selection(workflow_id, state))
        results.append(await self._eval_hallucination(workflow_id, state))

        for agent_name, output in state.get("agent_outputs", {}).items():
            results.append(await self._eval_agent_accuracy(workflow_id, agent_name, output))

        return results

    async def _eval_json_validity(
        self, workflow_id: uuid.UUID, state: dict[str, Any]
    ) -> dict[str, Any]:
        valid_count = 0
        total = 0
        for name, output in state.get("agent_outputs", {}).items():
            total += 1
            result = output.get("result", {}) if isinstance(output, dict) else {}
            if isinstance(result, dict) and not result.get("parse_error"):
                valid_count += 1

        passed = valid_count == total if total > 0 else True
        score = valid_count / total if total > 0 else 1.0

        await self.repo.create(
            workflow_run_id=workflow_id,
            evaluation_type=EvaluationType.JSON_VALIDITY,
            target="all_agents",
            score=score,
            passed=passed,
            details={"valid": valid_count, "total": total},
        )
        return {"type": "json_validity", "passed": passed, "score": score}

    async def _eval_workflow_correctness(
        self, workflow_id: uuid.UUID, state: dict[str, Any]
    ) -> dict[str, Any]:
        expected_agents = {"planner", "audit", "reporting"}
        executed = set(state.get("agent_outputs", {}).keys())
        missing = expected_agents - executed
        passed = len(missing) == 0
        score = len(executed & expected_agents) / len(expected_agents)

        await self.repo.create(
            workflow_run_id=workflow_id,
            evaluation_type=EvaluationType.WORKFLOW_CORRECTNESS,
            target="workflow",
            score=score,
            passed=passed,
            details={"missing_agents": list(missing), "executed": list(executed)},
        )
        return {"type": "workflow_correctness", "passed": passed, "score": score}

    async def _eval_tool_selection(
        self, workflow_id: uuid.UUID, state: dict[str, Any]
    ) -> dict[str, Any]:
        tool_outputs = state.get("tool_outputs", [])
        passed = True
        score = 1.0

        await self.repo.create(
            workflow_run_id=workflow_id,
            evaluation_type=EvaluationType.TOOL_SELECTION,
            target="tools",
            score=score,
            passed=passed,
            details={"tool_calls": len(tool_outputs)},
        )
        return {"type": "tool_selection", "passed": passed, "score": score}

    async def _eval_agent_accuracy(
        self, workflow_id: uuid.UUID, agent_name: str, output: Any
    ) -> dict[str, Any]:
        confidence = output.get("confidence", 0) if isinstance(output, dict) else 0
        passed = confidence >= 0.5

        await self.repo.create(
            workflow_run_id=workflow_id,
            evaluation_type=EvaluationType.AGENT_ACCURACY,
            target=agent_name,
            score=confidence,
            passed=passed,
        )
        return {"type": "agent_accuracy", "agent": agent_name, "passed": passed, "score": confidence}

    async def _eval_hallucination(
        self, workflow_id: uuid.UUID, state: dict[str, Any]
    ) -> dict[str, Any]:
        indicators = []
        for name, output in state.get("agent_outputs", {}).items():
            result = output.get("result", {}) if isinstance(output, dict) else {}
            if result.get("parse_error"):
                indicators.append(f"{name}: JSON parse failure")
            if result.get("raw_response"):
                indicators.append(f"{name}: unstructured response")

        passed = len(indicators) == 0
        score = 1.0 - (len(indicators) * 0.2)

        await self.repo.create(
            workflow_run_id=workflow_id,
            evaluation_type=EvaluationType.HALLUCINATION,
            target="all_agents",
            score=max(score, 0),
            passed=passed,
            details={"indicators": indicators},
        )
        return {"type": "hallucination", "passed": passed, "indicators": indicators}

    async def get_evaluations(self, workflow_id: uuid.UUID) -> list[dict[str, Any]]:
        records = await self.repo.list_by_workflow(workflow_id)
        return [
            {
                "type": r.evaluation_type,
                "target": r.target,
                "score": r.score,
                "passed": r.passed,
                "details": r.details,
            }
            for r in records
        ]
