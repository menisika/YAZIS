from fastapi import APIRouter

from src.dispatch.analytics.views import router as analytics_router
from src.dispatch.auth.views import router as auth_router
from src.dispatch.chat.views import router as chat_router
from src.dispatch.exercise.views import router as exercise_router
from src.dispatch.session.views import router as session_router
from src.dispatch.user.views import router as user_router
from src.dispatch.workout.views import router as workout_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(exercise_router)
api_router.include_router(workout_router)
api_router.include_router(session_router)
api_router.include_router(analytics_router)
api_router.include_router(chat_router)
