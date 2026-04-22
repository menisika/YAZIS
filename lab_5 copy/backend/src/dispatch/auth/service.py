import json
from pathlib import Path

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials
from sqlmodel import Session, select

from src.dispatch.config import settings
from src.dispatch.user.models import User

_firebase_initialized = False


def _init_firebase():
    global _firebase_initialized
    if not _firebase_initialized:
        if not settings.firebase_project_id:
            raise ValueError("Firebase project ID is not configured")

        if not firebase_admin._apps:
            options = {"projectId": settings.firebase_project_id}
            credential = None

            if settings.firebase_service_account_key:
                try:
                    service_account = json.loads(settings.firebase_service_account_key)
                except json.JSONDecodeError as e:
                    raise ValueError("Firebase service account key is not valid JSON") from e
                credential = credentials.Certificate(service_account)
            else:
                key_path = Path(settings.firebase_service_account_key_path)
                if key_path.exists():
                    credential = credentials.Certificate(str(key_path))

            if credential is not None:
                firebase_admin.initialize_app(credential, options)
            else:
                firebase_admin.initialize_app(options=options)

        _firebase_initialized = True


def verify_firebase_token(token: str) -> dict:
    """Verify a Firebase ID token and return the decoded claims."""
    _init_firebase()
    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded
    except Exception as e:
        raise ValueError(f"Invalid Firebase token: {e}") from e


def get_or_create_user(*, db_session: Session, firebase_uid: str, email: str, display_name: str | None = None) -> User:
    """Find existing user by firebase_uid or create a new one."""
    statement = select(User).where(User.firebase_uid == firebase_uid)
    user = db_session.exec(statement).first()

    if not user:
        user = User(
            firebase_uid=firebase_uid,
            email=email,
            display_name=display_name,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    return user
