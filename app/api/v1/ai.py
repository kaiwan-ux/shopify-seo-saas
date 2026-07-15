from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.core.exceptions import NotFoundError
from app.dependencies.auth import CurrentUserDep, SessionDep
from app.dependencies.services import AIServiceDep, ShopifyServiceDep
from app.evaluation.evaluator import WorkflowEvaluator
from app.models.memory_entry import MemoryType
from app.prompts.manager import PromptManager
from app.repositories.store import StoreRepository
from app.workflows.orchestrator import WorkflowOrchestrator

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    store_id: UUID | None = None


class ChatResponse(BaseModel):
    type: str
    message: str
    workflow: dict | None = None
    tokens_used: int | None = None
    latency_ms: int | None = None


class WorkflowStartRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=5000)
    store_id: UUID | None = None


class AgentRunRequest(BaseModel):
    agent_name: str = Field(
        ...,
        pattern="^(planner|audit|content|technical|performance|autofix|monitoring|reporting)$",
    )
    task: str = Field(..., min_length=1, max_length=5000)
    store_id: UUID | None = None


class ApplyFixesRequest(BaseModel):
    fixes: list[dict] = Field(default_factory=list, max_length=500)
    store_id: UUID | None = None


async def _resolve_store(current_user, store_id: UUID | None, session, shopify_service):
    if store_id:
        store = await StoreRepository(session).get_by_id(store_id)
        if store is None or store.owner_id != current_user.id:
            raise NotFoundError("Store not found")
        return store
    return await shopify_service.get_user_store(current_user)


@router.post("/chat", response_model=ChatResponse, summary="Chat with AI assistant")
async def ai_chat(
    data: ChatRequest,
    current_user: CurrentUserDep,
    ai_service: AIServiceDep,
) -> ChatResponse:
    result = await ai_service.chat(current_user.id, data.message, data.store_id)
    return ChatResponse(**result)


@router.post("/workflow/start", summary="Start a SEO workflow")
async def start_workflow(
    data: WorkflowStartRequest,
    current_user: CurrentUserDep,
    ai_service: AIServiceDep,
    shopify_service: ShopifyServiceDep,
    session: SessionDep,
):
    store = await _resolve_store(current_user, data.store_id, session, shopify_service)
    return await ai_service.start_workflow(current_user.id, store.id, data.task)


@router.post("/agents/run", summary="Run a single agent")
async def run_agent(
    data: AgentRunRequest,
    current_user: CurrentUserDep,
    ai_service: AIServiceDep,
    shopify_service: ShopifyServiceDep,
    session: SessionDep,
):
    store = await _resolve_store(current_user, data.store_id, session, shopify_service)
    return await ai_service.run_agent(data.agent_name, current_user.id, store.id, data.task)




@router.post("/approvals/apply", summary="Apply approved SEO fixes")
async def apply_approved_fixes(
    data: ApplyFixesRequest,
    current_user: CurrentUserDep,
    shopify_service: ShopifyServiceDep,
    session: SessionDep,
):
    from app.agents.shared.models import AgentContext, AgentOutput, NextAction
    from app.agents.shared.registry import create_agent

    store = await _resolve_store(current_user, data.store_id, session, shopify_service)
    context = AgentContext(
        workflow_id=str(UUID(int=0)),
        user_id=str(current_user.id),
        store_id=str(store.id),
        task="Apply approved SEO fixes",
        agent_outputs={
            "content": AgentOutput(
                agent_name="content",
                reasoning="User-approved SEO fixes",
                result={"optimizations": data.fixes},
                confidence=1.0,
                next_action=NextAction.CONTINUE,
            )
        },
    )
    output = await create_agent("autofix", session).run(context)
    return output.model_dump()


@router.get("/workflow/{workflow_id}", summary="Get workflow status and results")
async def get_workflow(
    workflow_id: UUID,
    current_user: CurrentUserDep,
    ai_service: AIServiceDep,
):
    result = await ai_service.get_workflow(workflow_id)
    if result is None:
        raise NotFoundError("Workflow not found")
    return result


@router.get("/agents", summary="List available AI agents")
async def list_agents():
    return {"agents": WorkflowOrchestrator.list_available_agents()}


@router.get("/memory", summary="Get user memory entries")
async def get_memory(
    current_user: CurrentUserDep,
    ai_service: AIServiceDep,
    memory_type: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
):
    mt = MemoryType(memory_type) if memory_type else None
    entries = await ai_service.memory.get_by_user(current_user.id, mt, limit)
    return {"items": entries, "total": len(entries)}


@router.get("/prompts", summary="List active prompt templates")
async def list_prompts(current_user: CurrentUserDep):
    manager = PromptManager()
    templates = manager.load_all_templates()
    return {
        "prompts": [
            {"name": t.name, "agent_name": t.agent_name, "version": t.version}
            for t in templates.values()
        ]
    }


@router.get("/evaluation/{workflow_id}", summary="Get workflow evaluation results")
async def get_evaluation(
    workflow_id: UUID,
    current_user: CurrentUserDep,
    ai_service: AIServiceDep,
):
    evaluator = WorkflowEvaluator(ai_service.session)
    results = await evaluator.get_evaluations(workflow_id)
    return {"workflow_id": str(workflow_id), "evaluations": results}
