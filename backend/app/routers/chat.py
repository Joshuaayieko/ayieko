"""Chat routes: send a message, list conversations and their messages."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..agents import PlannerAgent
from ..auth import get_current_user
from ..database import get_db
from ..memory import MemoryStore
from ..models import Conversation, Message, User
from ..schemas import (
    ChatRequest,
    ChatResponse,
    ConversationOut,
    MessageOut,
    ToolCallInfo,
)

router = APIRouter(prefix="/chat", tags=["chat"])

HISTORY_LIMIT = 20


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ChatResponse:
    # Resolve or create the conversation.
    if payload.conversation_id:
        conv = (
            db.query(Conversation)
            .filter(
                Conversation.id == payload.conversation_id,
                Conversation.user_id == user.id,
            )
            .first()
        )
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = Conversation(user_id=user.id, title=payload.message[:50] or "New chat")
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # Persist the user's message.
    db.add(Message(conversation_id=conv.id, role="user", content=payload.message))
    db.commit()

    # Build history for the LLM.
    history = [
        {"role": m.role, "content": m.content}
        for m in conv.messages[-HISTORY_LIMIT:]
        if m.role in ("user", "assistant")
    ]

    memory = MemoryStore(db, user.id)
    memory.extract_and_store(payload.message)

    planner = PlannerAgent(memory=memory)
    result = planner.handle(payload.message, history=history)

    # Persist the assistant reply.
    db.add(Message(conversation_id=conv.id, role="assistant", content=result.reply))
    db.commit()

    return ChatResponse(
        conversation_id=conv.id,
        reply=result.reply,
        plan=result.plan,
        tools_used=[
            ToolCallInfo(
                name=t["name"], arguments=t["arguments"], result=t["result"]
            )
            for t in result.tools_used
        ],
    )


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )


@router.get("/conversations/{conversation_id}", response_model=list[MessageOut])
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv.messages
