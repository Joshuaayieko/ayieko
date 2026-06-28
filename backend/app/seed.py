"""Seed the admin user from environment configuration on startup."""

import logging

from sqlalchemy.orm import Session

from .auth import hash_password
from .config import settings
from .database import SessionLocal
from .models import User

logger = logging.getLogger("orbes.seed")


def seed_admin() -> None:
    """Create (or promote) the configured admin account if it doesn't exist."""
    db: Session = SessionLocal()
    try:
        email = settings.orbes_admin_email.strip().lower()
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            if not existing.is_admin:
                existing.is_admin = True
                db.commit()
                logger.info("Promoted existing user %s to admin.", email)
            return

        admin = User(
            email=email,
            full_name="Orbes Admin",
            hashed_password=hash_password(settings.orbes_admin_password),
            is_admin=True,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        logger.info("Seeded admin account: %s", email)
    finally:
        db.close()
