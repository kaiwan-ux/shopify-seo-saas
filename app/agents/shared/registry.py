"""Agent registry — maps agent names to classes."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.audit.agent import AuditAgent
from app.agents.autofix.agent import AutoFixAgent
from app.agents.content.agent import ContentAgent
from app.agents.monitoring.agent import MonitoringAgent
from app.agents.performance.agent import PerformanceAgent
from app.agents.planner.agent import PlannerAgent
from app.agents.reporting.agent import ReportingAgent
from app.agents.shared.base import BaseAgent
from app.agents.shared.models import AgentName
from app.agents.technical.agent import TechnicalAgent

AGENT_CLASSES: dict[str, type[BaseAgent]] = {
    AgentName.PLANNER: PlannerAgent,
    AgentName.AUDIT: AuditAgent,
    AgentName.CONTENT: ContentAgent,
    AgentName.TECHNICAL: TechnicalAgent,
    AgentName.PERFORMANCE: PerformanceAgent,
    AgentName.AUTOFIX: AutoFixAgent,
    AgentName.MONITORING: MonitoringAgent,
    AgentName.REPORTING: ReportingAgent,
}


def create_agent(name: str, session: AsyncSession) -> BaseAgent:
    """Factory to instantiate an agent by name."""
    cls = AGENT_CLASSES.get(name)
    if cls is None:
        raise ValueError(f"Unknown agent: {name}")
    return cls(session)


def list_agents() -> list[dict[str, str]]:
    """Return metadata for all registered agents."""
    descriptions = {
        "planner": "Orchestrates workflow — breaks tasks into subtasks and selects agents",
        "audit": "Analyzes store data and detects SEO issues (read-only)",
        "content": "Generates SEO titles, descriptions, and content optimizations",
        "technical": "Technical SEO analysis — URLs, redirects, sitemaps",
        "performance": "Core Web Vitals and performance optimization",
        "autofix": "Executes approved fixes via the tool layer",
        "monitoring": "Detects regressions and compares historical audits",
        "reporting": "Generates human-readable reports and dashboard data",
    }
    return [{"name": name, "description": descriptions.get(name, "")} for name in AGENT_CLASSES]
