"""Workflow orchestration service."""

import time
import uuid
from datetime import UTC, datetime
from typing import Any

from langgraph.graph.state import CompiledStateGraph
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.shared.models import AgentContext, AgentOutput
from app.agents.shared.registry import create_agent, list_agents
from app.evaluation.evaluator import WorkflowEvaluator
from app.graphs.seo_workflow import build_seo_workflow
from app.memory.service import MemoryService
from app.models.workflow_run import WorkflowStatus
from app.repositories.agent_run import AgentRunRepository
from app.repositories.workflow_run import WorkflowRunRepository
from app.state.workflow_state import WorkflowState


class WorkflowOrchestrator:
    """Manages LangGraph workflow lifecycle."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.workflow_repo = WorkflowRunRepository(session)
        self.agent_run_repo = AgentRunRepository(session)
        self.memory = MemoryService(session)
        self.evaluator = WorkflowEvaluator(session)
        self._graph: CompiledStateGraph | None = None

    def _get_graph(self) -> CompiledStateGraph:
        if self._graph is None:
            graph = build_seo_workflow(self.session)
            self._graph = graph.compile()
        return self._graph

    async def start_workflow(
        self,
        user_id: uuid.UUID,
        store_id: uuid.UUID,
        task: str,
    ) -> dict[str, Any]:
        """Start a new SEO workflow."""
        workflow_run = await self.workflow_repo.create_run(
            user_id=user_id,
            store_id=store_id,
            task=task,
        )

        initial_state: WorkflowState = {
            "workflow_id": str(workflow_run.id),
            "user_id": str(user_id),
            "store_id": str(store_id),
            "task": task,
            "status": WorkflowStatus.RUNNING,
            "agent_outputs": {},
            "tool_outputs": [],
            "errors": [],
            "retry_count": 0,
            "max_retries": 3,
            "logs": [],
            "total_tokens": 0,
            "approval_status": "none",
            "pending_approvals": [],
            "approved_fixes": [],
            "current_step": 0,
            "execution_order": [],
        }

        start = time.perf_counter()
        workflow_run.started_at = datetime.now(UTC)
        await self.session.flush()

        try:
            graph = self._get_graph()
            final_state = await graph.ainvoke(initial_state)

            duration_ms = int((time.perf_counter() - start) * 1000)
            status = final_state.get("status", WorkflowStatus.COMPLETED)

            await self.workflow_repo.complete(
                workflow_run,
                status=status,
                graph_state=final_state,
                duration_ms=duration_ms,
            )

            try:
                await self._persist_agent_runs(workflow_run.id, final_state)
            except Exception as exc:
                logger.warning("Workflow {} agent-run persistence skipped: {}", workflow_run.id, exc)

            try:
                await self.memory.store_workflow_memory(workflow_run.id, store_id, final_state)
            except Exception as exc:
                logger.warning("Workflow {} memory persistence skipped: {}", workflow_run.id, exc)

            try:
                await self.evaluator.evaluate_workflow(workflow_run.id, final_state)
            except Exception as exc:
                logger.warning("Workflow {} evaluation skipped: {}", workflow_run.id, exc)

            logger.info("Workflow {} completed in {}ms status={}", workflow_run.id, duration_ms, status)

            return {
                "workflow_id": str(workflow_run.id),
                "status": status,
                "approval_status": final_state.get("approval_status"),
                "pending_approvals": final_state.get("pending_approvals", []),
                "approved_fixes": final_state.get("approved_fixes", []),
                "logs": final_state.get("logs", []),
                "report": final_state.get("report"),
                "agent_outputs": final_state.get("agent_outputs", {}),
                "duration_ms": duration_ms,
            }

        except Exception as exc:
            await self.workflow_repo.fail(workflow_run, str(exc))
            logger.exception("Workflow {} failed: {}", workflow_run.id, exc)
            raise

    async def get_workflow(self, workflow_id: uuid.UUID) -> dict[str, Any] | None:
        run = await self.workflow_repo.get_by_id(workflow_id)
        if run is None:
            return None
        agent_runs = await self.agent_run_repo.list_by_workflow(workflow_id)
        return {
            "id": str(run.id),
            "status": run.status,
            "task": run.task,
            "store_id": str(run.store_id),
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "duration_ms": run.duration_ms,
            "graph_state": run.graph_state,
            "agent_runs": [
                {
                    "agent_name": ar.agent_name,
                    "status": ar.status,
                    "confidence": ar.confidence,
                    "duration_ms": ar.duration_ms,
                }
                for ar in agent_runs
            ],
        }

    async def run_single_agent(
        self,
        agent_name: str,
        user_id: uuid.UUID,
        store_id: uuid.UUID,
        task: str,
    ) -> dict[str, Any]:
        """Run a single agent independently."""
        context = AgentContext(
            workflow_id=str(uuid.uuid4()),
            user_id=str(user_id),
            store_id=str(store_id),
            task=task,
        )
        agent = create_agent(agent_name, self.session)
        output = await agent.run(context)
        return output.model_dump()

    async def _persist_agent_runs(
        self, workflow_id: uuid.UUID, state: dict[str, Any]
    ) -> None:
        for name, output_data in state.get("agent_outputs", {}).items():
            output = AgentOutput(**output_data) if isinstance(output_data, dict) else output_data
            await self.agent_run_repo.create_run(
                workflow_run_id=workflow_id,
                agent_name=name,
                output=output,
            )

    @staticmethod
    def list_available_agents() -> list[dict[str, str]]:
        return list_agents()
