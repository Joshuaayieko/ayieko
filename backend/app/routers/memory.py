"""Memory routes: list, add and delete what Orbes remembers about the user."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..memory import MemoryStore
from ..models import User
from ..schemas import MemoryCreate, MemoryOut

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("", response_model=list[MemoryOut])
def list_memories(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return MemoryStore(db, user.id).all()


@router.post("", response_model=MemoryOut)
def add_memory(
    payload: MemoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return MemoryStore(db, user.id).remember(
        key=payload.key, value=payload.value, category=payload.category
    )


@router.delete("/{memory_id}", status_code=204)
def delete_memory(
    memory_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not MemoryStore(db, user.id).forget(memory_id):
        raise HTTPException(status_code=404, detail="Memory not found")
