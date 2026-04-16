import logging

from googleapiclient.discovery import build
from sqlmodel import Session

from src.dispatch.config import settings
from src.dispatch.exercise.models import Exercise

logger = logging.getLogger(__name__)


def search_youtube_video(exercise_name: str) -> str | None:
    if not settings.youtube_api_key:
        logger.warning("YOUTUBE_API_KEY not set, skipping video search")
        return None

    try:
        youtube = build("youtube", "v3", developerKey=settings.youtube_api_key)
        response = (
            youtube.search()
            .list(
                q=f"{exercise_name} exercise tutorial",
                type="video",
                videoDuration="short",
                order="relevance",
                maxResults=3,
                part="snippet",
            )
            .execute()
        )
        items = response.get("items", [])
        if items:
            return items[0]["id"]["videoId"]
    except Exception:
        logger.exception("YouTube API search failed for '%s'", exercise_name)

    return None


def get_or_fetch_video_id(*, db_session: Session, exercise: Exercise) -> str | None:
    if exercise.youtube_video_id:
        return exercise.youtube_video_id

    video_id = search_youtube_video(exercise.name)
    if video_id:
        exercise.youtube_video_id = video_id
        db_session.add(exercise)
        db_session.commit()
        db_session.refresh(exercise)

    return video_id
