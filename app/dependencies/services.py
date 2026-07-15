from typing import Annotated

from fastapi import Depends

from app.dependencies.auth import SessionDep
from app.integrations.mcp.executor import MCPToolExecutor
from app.integrations.shopify.services import ShopifyIntegrationService
from app.services.ai import AIService
from app.services.auth import AuthService
from app.services.user import UserService


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)


def get_user_service(session: SessionDep) -> UserService:
    return UserService(session)


def get_shopify_service(session: SessionDep) -> ShopifyIntegrationService:
    return ShopifyIntegrationService(session)


def get_mcp_executor(session: SessionDep) -> MCPToolExecutor:
    return MCPToolExecutor(session)


def get_ai_service(session: SessionDep) -> AIService:
    return AIService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
ShopifyServiceDep = Annotated[ShopifyIntegrationService, Depends(get_shopify_service)]
MCPToolExecutorDep = Annotated[MCPToolExecutor, Depends(get_mcp_executor)]
AIServiceDep = Annotated[AIService, Depends(get_ai_service)]
