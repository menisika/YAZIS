from fastapi import APIRouter, Query

from src.dispatch.auth.permissions import CurrentUser
from src.dispatch.database import SessionDep
from src.dispatch.exceptions import NotFoundError
from src.dispatch.exercise.models import Exercise
from src.dispatch.session import service as session_service
from src.dispatch.session.models import (
    SessionCreate,
    SessionRead,
    SessionSetCreate,
    SessionSetRead,
    SessionUpdate,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _enrich_set(st, db_session) -> SessionSetRead:
    exercise = db_session.get(Exercise, st.exercise_id)
    return SessionSetRead(
        **st.model_dump(),
        exercise_name=exercise.name if exercise else None,
    )


@router.post("", response_model=SessionRead)
def start_session(
    body: SessionCreate,
    current_user: CurrentUser,
    db_session: SessionDep,
):
    ws = session_service.create(
        db_session=db_session, user_id=current_user.id, session_in=body
    )
    return SessionRead(**ws.model_dump(), sets=[])


@router.get("", response_model=list[SessionRead])
def list_sessions(
    current_user: CurrentUser,
    db_session: SessionDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    sessions = session_service.get_all(
        db_session=db_session, user_id=current_user.id, offset=offset, limit=limit
    )
    result = []
    for s in sessions:
        sets = [_enrich_set(st, db_session) for st in (s.sets or [])]
        result.append(SessionRead(**s.model_dump(), sets=sets))
    return result


@router.get("/{session_id}", response_model=SessionRead)
def get_session(session_id: int, current_user: CurrentUser, db_session: SessionDep):
    ws = session_service.get(db_session=db_session, session_id=session_id)
    if not ws or ws.user_id != current_user.id:
        raise NotFoundError("Session not found")
    sets = [_enrich_set(st, db_session) for st in (ws.sets or [])]
    return SessionRead(**ws.model_dump(), sets=sets)


@router.patch("/{session_id}", response_model=SessionRead)
def update_session(
    session_id: int,
    body: SessionUpdate,
    current_user: CurrentUser,
    db_session: SessionDep,
):
    ws = session_service.update(
        db_session=db_session,
        session_id=session_id,
        user_id=current_user.id,
        session_in=body,
    )
    sets = [_enrich_set(st, db_session) for st in (ws.sets or [])]
    return SessionRead(**ws.model_dump(), sets=sets)


@router.post("/{session_id}/sets", response_model=SessionSetRead)
def log_set(
    session_id: int,
    body: SessionSetCreate,
    current_user: CurrentUser,
    db_session: SessionDep,
):
    s = session_service.log_set(
        db_session=db_session,
        session_id=session_id,
        user_id=current_user.id,
        set_in=body,
    )
    return _enrich_set(s, db_session)


@router.delete("/{session_id}/sets/{set_id}")
def delete_set(
    session_id: int,
    set_id: int,
    current_user: CurrentUser,
    db_session: SessionDep,
):
    session_service.delete_set(
        db_session=db_session,
        session_id=session_id,
        set_id=set_id,
        user_id=current_user.id,
    )
    return {"ok": True}
