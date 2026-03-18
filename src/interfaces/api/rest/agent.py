"""Agent 自主注册接口 - 向 cultrue 注册并保存凭证"""

from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models.agent_credential_model import AgentCredentialModel
from src.interfaces.api.schemas import ApiResponse
from src.interfaces.api.dependencies import get_db_session, get_settings

router = APIRouter(prefix="/api/agent", tags=["agent"])


class AgentRegisterRequest(BaseModel):
    agent_id: str = Field(..., description="Agent ID，格式：agent_xxx")
    name: str = Field(..., min_length=1, max_length=100)
    avatar: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    system_prompt: Optional[str] = Field(default=None)


class AgentRegisterResponse(BaseModel):
    agent_id: str
    api_key: str
    name: str
    avatar: Optional[str] = None
    description: Optional[str] = None
    message: str = "注册成功，请妥善保存 api_key，此后不再显示"


@router.post("/register", response_model=ApiResponse[AgentRegisterResponse])
async def register_to_cultrue(
    request: AgentRegisterRequest,
    db: AsyncSession = Depends(get_db_session),
    settings=Depends(get_settings),
):
    """向 cultrue 注册 agent，并将 agent_id 和 api_key 保存到本地数据库"""

    # 1. 调用 cultrue 注册接口
    cultrue_url = f"{settings.cultrue_base_url}/api/agents/register"
    payload = {
        "agent_id": request.agent_id,
        "name": request.name,
        "avatar": request.avatar,
        "description": request.description,
        "system_prompt": request.system_prompt,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(cultrue_url, json=payload)
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="无法连接到 cultrue 服务")

    if resp.status_code not in (200, 201):
        try:
            detail = resp.json().get("message", resp.text)
        except Exception:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=f"cultrue 注册失败: {detail}")

    body = resp.json()
    if body.get("code") not in (200, 201):
        raise HTTPException(status_code=400, detail=body.get("message", "注册失败"))

    data = body["data"]
    api_key: str = data["api_key"]
    agent_info: dict = data["agent"]

    # 2. 保存凭证到本地 DB（upsert：已存在则更新 api_key）
    from sqlalchemy import select
    stmt = select(AgentCredentialModel).where(
        AgentCredentialModel.agent_id == request.agent_id
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.api_key = api_key
        existing.name = request.name
        existing.avatar = request.avatar
        existing.description = request.description
    else:
        credential = AgentCredentialModel(
            agent_id=request.agent_id,
            api_key=api_key,
            name=request.name,
            avatar=request.avatar,
            description=request.description,
        )
        db.add(credential)

    await db.commit()

    return ApiResponse.success(
        data=AgentRegisterResponse(
            agent_id=request.agent_id,
            api_key=api_key,
            name=request.name,
            avatar=request.avatar,
            description=request.description,
        ),
        message="注册成功",
    )


@router.get("/credentials", response_model=ApiResponse[list])
async def get_credentials(
    db: AsyncSession = Depends(get_db_session),
):
    """查看本地保存的所有 agent 凭证（api_key 脱敏）"""
    from sqlalchemy import select
    result = await db.execute(select(AgentCredentialModel))
    rows = result.scalars().all()
    return ApiResponse.success(data=[
        {
            "agent_id": r.agent_id,
            "name": r.name,
            "avatar": r.avatar,
            "api_key_masked": r.api_key[:10] + "..." + r.api_key[-4:] if r.api_key else None,
            "registered_at": r.registered_at.isoformat(),
        }
        for r in rows
    ])
