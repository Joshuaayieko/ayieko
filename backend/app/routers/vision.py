"""Vision route: analyse an uploaded image."""

import base64

from fastapi import APIRouter, Depends, File, Form, UploadFile

from ..agents.vision_agent import VisionAgent
from ..auth import get_current_user
from ..models import User

router = APIRouter(prefix="/vision", tags=["vision"])
_agent = VisionAgent()


@router.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    prompt: str = Form("Describe this image."),
    _: User = Depends(get_current_user),
):
    data = await file.read()
    b64 = base64.b64encode(data).decode()
    media_type = file.content_type or "image/png"
    return {"result": _agent.analyze(b64, media_type, prompt)}
