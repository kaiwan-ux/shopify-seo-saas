"""LangGraph SEO workflow definition."""

from typing import Any, Literal

from langgraph.graph import END, StateGraph
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.shared.models import AgentContext, AgentOutput, NextAction
from app.agents.shared.registry import create_agent
from app.policies.approval import ApprovalPolicy
from app.state.workflow_state import WorkflowState


def build_seo_workflow(session: AsyncSession) -> StateGraph:
    """Build the production LangGraph SEO workflow."""

    approval_policy = ApprovalPolicy()

    async def run_agent_node(state: WorkflowState, agent_name: str) -> dict[str, Any]:
        """Generic node that runs any agent."""
        context = AgentContext(
            workflow_id=state["workflow_id"],
            user_id=state["user_id"],
            store_id=state["store_id"],
            task=state["task"],
            agent_outputs={
                name: AgentOutput(**output)
                for name, output in state.get("agent_outputs", {}).items()
            },
        )

        agent = create_agent(agent_name, session)
        output = await agent.run(context)

        agent_outputs = dict(state.get("agent_outputs", {}))
        agent_outputs[agent_name] = output.model_dump()

        logs = list(state.get("logs", []))
        logs.append(f"Agent {agent_name} completed: {output.next_action}")

        return {
            "agent_outputs": agent_outputs,
            "current_agent": agent_name,
            "logs": logs,
        }

    async def planner_node(state: WorkflowState) -> dict[str, Any]:
        result = await run_agent_node(state, "planner")
        plan = result["agent_outputs"].get("planner", {}).get("result", {})
        execution_order = plan.get("execution_order", [
            "audit", "technical", "performance", "content", "reporting", "monitoring",
        ])
        return {
            **result,
            "execution_plan": plan.get("plan"),
            "execution_order": execution_order,
            "current_step": 0,
            "status": "running",
        }

    async def audit_node(state: WorkflowState) -> dict[str, Any]:
        return await run_agent_node(state, "audit")

    async def technical_node(state: WorkflowState) -> dict[str, Any]:
        return await run_agent_node(state, "technical")

    async def performance_node(state: WorkflowState) -> dict[str, Any]:
        return await run_agent_node(state, "performance")

    async def content_node(state: WorkflowState) -> dict[str, Any]:
        return await run_agent_node(state, "content")

    async def approval_node(state: WorkflowState) -> dict[str, Any]:
        content_output = state.get("agent_outputs", {}).get("content", {})
        optimizations = content_output.get("result", {}).get("optimizations", [])

        if approval_policy.requires_approval_for_fixes(optimizations):
            return {
                "approval_status": "pending",
                "status": "waiting_approval",
                "pending_approvals": optimizations,
            }

        return {
            "approval_status": "auto_approved",
            "approved_fixes": optimizations,
        }

    async def autofix_node(state: WorkflowState) -> dict[str, Any]:
        if state.get("approval_status") == "pending":
            return {"status": "waiting_approval"}
        return await run_agent_node(state, "autofix")

    async def reporting_node(state: WorkflowState) -> dict[str, Any]:
        result = await run_agent_node(state, "reporting")
        report = result["agent_outputs"].get("reporting", {}).get("result")
        return {**result, "report": report}

    async def monitoring_node(state: WorkflowState) -> dict[str, Any]:
        result = await run_agent_node(state, "monitoring")
        final_status = "waiting_approval" if state.get("approval_status") == "pending" else "completed"
        return {**result, "status": final_status}

    def route_after_approval(state: WorkflowState) -> Literal["autofix", "reporting"]:
        if state.get("approval_status") == "pending":
            return "reporting"
        return "autofix"

    graph = StateGraph(WorkflowState)

    graph.add_node("planner", planner_node)
    graph.add_node("audit", audit_node)
    graph.add_node("technical", technical_node)
    graph.add_node("performance", performance_node)
    graph.add_node("content", content_node)
    graph.add_node("approval", approval_node)
    graph.add_node("autofix", autofix_node)
    graph.add_node("reporting", reporting_node)
    graph.add_node("monitoring", monitoring_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "audit")
    graph.add_edge("audit", "technical")
    graph.add_edge("technical", "performance")
    graph.add_edge("performance", "content")
    graph.add_edge("content", "approval")
    graph.add_conditional_edges("approval", route_after_approval, {
        "autofix": "autofix",
        "reporting": "reporting",
    })
    graph.add_edge("autofix", "reporting")
    graph.add_edge("reporting", "monitoring")
    graph.add_edge("monitoring", END)

    return graph
