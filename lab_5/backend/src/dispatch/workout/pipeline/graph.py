"""3-node LangGraph pipeline: Architect → Librarian → Persist."""

from __future__ import annotations

import json
import logging
from datetime import date, timedelta
from difflib import SequenceMatcher

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from sqlmodel import Session, select

from src.dispatch.config import settings
from src.dispatch.exercise import service as exercise_service
from src.dispatch.user.models import UserProfile
from src.dispatch.workout import service as workout_service
from src.dispatch.workout.pipeline.prompts import ARCHITECT_PROMPT, LIBRARIAN_PROMPT
from src.dispatch.workout.pipeline.schemas import (
    ExerciseBatchSchema,
    PipelineState,
    WeeklyPlanSchema,
)

logger = logging.getLogger(__name__)


def _make_llm(temperature: float = 0.3) -> ChatGroq:
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        api_key=settings.groq_api_key,
    )


def _slugify(name: str) -> str:
    """Delegate to exercise service slugify."""
    return exercise_service.slugify(name)


def build_pipeline(db_session: Session):
    """Return a compiled LangGraph pipeline capturing db_session in closures."""

    # ── Node 1: Plan Architect ────────────────────────────────────────────────

    def plan_architect_node(state: PipelineState) -> dict:
        llm = _make_llm(temperature=0.5)
        structured_llm = llm.with_structured_output(WeeklyPlanSchema)

        existing_names: list[str] = state.get("existing_names", [])
        catalog_hint = ""
        if existing_names:
            sample = existing_names[:150]  # cap to avoid token bloat
            catalog_hint = (
                "\n\nExercises already in the library — prefer reusing these exact names "
                "when semantically equivalent:\n"
                + "\n".join(f"- {n}" for n in sample)
            )

        messages = [
            SystemMessage(content=ARCHITECT_PROMPT + catalog_hint),
            HumanMessage(
                content=(
                    f"User profile: {state.get('user_profile_json', '{}')}\n"
                    f"Week start: {state['week_start']}\n"
                    f"Preferences: {json.dumps(state.get('preferences', {}))}"
                )
            ),
        ]

        plan: WeeklyPlanSchema = structured_llm.invoke(messages)

        # Ensure exactly 7 days (pad with rest if model produced fewer)
        covered = {d.day_of_week for d in plan.days}
        for dow in range(7):
            if dow not in covered:
                from src.dispatch.workout.pipeline.schemas import PlannedDay
                plan.days.append(PlannedDay(day_of_week=dow, focus="Rest", is_rest=True))
        plan.days.sort(key=lambda d: d.day_of_week)

        # Post-generation dedup pass: rename to existing names when close enough
        if existing_names:
            slug_to_name = {_slugify(n): n for n in existing_names}
            existing_lower = [n.lower() for n in existing_names]

            for day in plan.days:
                for ex in day.exercises:
                    ex_slug = _slugify(ex.name)
                    if ex_slug in slug_to_name:
                        ex.name = slug_to_name[ex_slug]
                    else:
                        ex_lower = ex.name.lower()
                        ratios = [
                            SequenceMatcher(None, ex_lower, el).ratio()
                            for el in existing_lower
                        ]
                        best_idx = max(range(len(ratios)), key=lambda i: ratios[i])
                        if ratios[best_idx] >= 0.85:
                            ex.name = existing_names[best_idx]

        logger.info(
            "Architect: planned %d training days",
            sum(1 for d in plan.days if not d.is_rest),
        )
        return {"weekly_plan": plan}

    # ── Node 2: Exercise Librarian ────────────────────────────────────────────

    def exercise_librarian_node(state: PipelineState) -> dict:
        plan: WeeklyPlanSchema = state["weekly_plan"]

        # Collect all unique exercise names across all training days
        all_names: dict[str, str] = {}  # slug → canonical name from plan
        for day in plan.days:
            for ex in day.exercises:
                all_names[_slugify(ex.name)] = ex.name

        if not all_names:
            return {"exercise_map": {}}

        # Look up existing exercises by slug
        existing_map = exercise_service.get_by_slugs(
            db_session=db_session, slugs=list(all_names.keys())
        )

        missing_names = [
            name
            for slug, name in all_names.items()
            if slug not in existing_map
        ]

        if missing_names:
            logger.info("Librarian: generating metadata for %d new exercises", len(missing_names))
            llm = _make_llm(temperature=0.2)
            structured_llm = llm.with_structured_output(ExerciseBatchSchema)

            messages = [
                SystemMessage(content=LIBRARIAN_PROMPT),
                HumanMessage(
                    content=(
                        "Generate metadata for these exercises:\n"
                        + "\n".join(f"- {n}" for n in missing_names)
                    )
                ),
            ]
            batch: ExerciseBatchSchema = structured_llm.invoke(messages)

            for gen_ex in batch.exercises:
                # Normalise slug in case the model drifted
                gen_ex.slug = _slugify(gen_ex.name)
                if gen_ex.slug in existing_map:
                    continue  # race condition guard
                try:
                    exercise = exercise_service.create_with_muscles(
                        db_session=db_session, data=gen_ex
                    )
                    existing_map[gen_ex.slug] = exercise
                    logger.info("Librarian: created exercise '%s'", gen_ex.name)
                except Exception:
                    logger.exception("Librarian: failed to create '%s'", gen_ex.name)
                    db_session.rollback()
                    # Recover: the exercise may already exist — look it up by name
                    recovered = exercise_service.get_by_name(
                        db_session=db_session, name=gen_ex.name
                    )
                    if recovered:
                        existing_map[gen_ex.slug] = recovered
                        logger.info("Librarian: recovered existing exercise '%s'", gen_ex.name)

        return {"exercise_map": existing_map}

    # ── Node 3: Persist ───────────────────────────────────────────────────────

    def persist_plan_node(state: PipelineState) -> dict:
        plan: WeeklyPlanSchema = state["weekly_plan"]
        exercise_map: dict = state["exercise_map"]
        user_id: int = state["user_id"]

        week_start = date.fromisoformat(state["week_start"])
        week_end = week_start + timedelta(days=6)

        # Delete previous plan (one-plan-per-user invariant)
        workout_service.delete_user_plan(db_session=db_session, user_id=user_id)

        # Build days_data in the format save_generated_plan expects
        days_data = []
        for idx, day in enumerate(plan.days):
            exercises_data = []
            for ex_idx, ex in enumerate(day.exercises):
                ex_slug = _slugify(ex.name)
                exercise = exercise_map.get(ex_slug)
                if exercise is None:
                    logger.warning("Persist: no Exercise row for '%s', skipping", ex.name)
                    continue
                exercises_data.append({
                    "exercise_id": exercise.id,
                    "sets": ex.sets,
                    "reps_min": ex.reps_min,
                    "reps_max": ex.reps_max,
                    "rest_seconds": ex.rest_seconds,
                    "order_index": ex_idx,
                    "notes": ex.notes or None,
                })

            days_data.append({
                "day_of_week": day.day_of_week,
                "focus": day.focus,
                "is_rest": day.is_rest,
                "exercises": exercises_data,
            })

        saved_plan = workout_service.save_generated_plan(
            db_session=db_session,
            user_id=user_id,
            name=plan.name,
            valid_from=week_start,
            valid_to=week_end,
            days_data=days_data,
        )

        result = workout_service.get_plan_read(
            db_session=db_session, plan_id=saved_plan.id
        )
        return {"result": result}

    # ── Assemble graph ────────────────────────────────────────────────────────

    graph = StateGraph(PipelineState)
    graph.add_node("architect", plan_architect_node)
    graph.add_node("librarian", exercise_librarian_node)
    graph.add_node("persist", persist_plan_node)
    graph.add_edge(START, "architect")
    graph.add_edge("architect", "librarian")
    graph.add_edge("librarian", "persist")
    graph.add_edge("persist", END)

    return graph.compile()
