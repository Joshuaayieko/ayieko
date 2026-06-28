"""Tool routes: introspect available tools and invoke them directly."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..auth import get_current_user
from ..models import User
from ..tools import default_registry

router = APIRouter(prefix="/tools", tags=["tools"])


class ToolInvocation(BaseModel):
    name: str
    arguments: dict = {}


@router.get("")
def list_tools(_: User = Depends(get_current_user)):
    return default_registry.schemas()


@router.post("/invoke")
def invoke_tool(payload: ToolInvocation, _: User = Depends(get_current_user)):
    result = default_registry.call(payload.name, **payload.arguments)
    return {"output": result.output, "client_action": result.client_action}
