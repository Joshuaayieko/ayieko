"""Memory store.

Structured memories (preferences, facts, projects) live in the SQL ``memories``
table. This module provides helpers to read/write them and to build a compact
context block that gets injected into the LLM prompt.

A vector store (ChromaDB / FAISS) can be slotted in later behind the same
interface for semantic recall over long conversation history.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import Memory


class MemoryStore:
    def __init__(self, db: Session, user_id: int) -> None:
        self.db = db
        self.user_id = user_id

    def remember(self, key: str, value: str, category: str = "general") -> Memory:
        """Upsert a memory by key for this user."""
        existing = (
            self.db.query(Memory)
            .filter(Memory.user_id == self.user_id, Memory.key == key)
            .first()
        )
        if existing:
            existing.value = value
            existing.category = category
            self.db.commit()
            self.db.refresh(existing)
            return existing

        memory = Memory(
            user_id=self.user_id, key=key, value=value, category=category
        )
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def all(self) -> list[Memory]:
        return (
            self.db.query(Memory)
            .filter(Memory.user_id == self.user_id)
            .order_by(Memory.created_at.desc())
            .all()
        )

    def forget(self, memory_id: int) -> bool:
        memory = (
            self.db.query(Memory)
            .filter(Memory.id == memory_id, Memory.user_id == self.user_id)
            .first()
        )
        if not memory:
            return False
        self.db.delete(memory)
        self.db.commit()
        return True

    def context_block(self, limit: int = 25) -> str:
        """Render known memories as a prompt-friendly string."""
        memories = self.all()[:limit]
        if not memories:
            return ""
        lines = [f"- ({m.category}) {m.key}: {m.value}" for m in memories]
        return "What you know about the user:\n" + "\n".join(lines)

    def extract_and_store(self, text: str) -> list[Memory]:
        """Heuristically capture simple 'remember that ...' style statements.

        This is intentionally lightweight; richer extraction can be delegated to
        the LLM later. Recognises patterns like:
            "remember that I like dark mode"
            "I prefer Python"
        """
        lowered = text.lower().strip()
        triggers = ("remember that ", "remember ", "note that ", "i prefer ", "i like ")
        for trig in triggers:
            if lowered.startswith(trig):
                fact = text[len(trig):].strip().rstrip(".")
                if fact:
                    return [self.remember(key=fact[:80], value=fact, category="preference")]
        return []
