"""Transactional PostgreSQL conversion from the PC's fea8b9182489 schema.

Run a dry run first; --apply retains every original table in an archive schema.
Stop the API and take a pg_dump backup before applying.
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path

import sqlalchemy as sa
from alembic.config import Config

from alembic import command
from app.core.database import Base, engine
from app.schemas.training import Prescription, SplitDayCreate

LEGACY_REVISION = "fea8b9182489"


def rows(conn, metadata, name):
    table = metadata[name]
    return [dict(row) for row in conn.execute(sa.select(table)).mappings()]


def insert_rows(conn, name, data):
    if data:
        conn.execute(Base.metadata.tables[name].insert(), data)


def transfer(conn, legacy):
    """Explicit conversion; original values remain in the archived schema."""
    now = datetime.now(timezone.utc)
    for name in ("users", "muscle_groups", "exercise_muscles"):
        if name == "exercise_muscles":
            continue  # Exercises must be copied first.
        insert_rows(conn, name, rows(conn, legacy, name))
    exercises = rows(conn, legacy, "exercises")
    codes = sorted({row["discipline"] for row in exercises})
    insert_rows(conn, "disciplines", [{"code": code, "name": code} for code in codes])
    for row in exercises:
        row.update(
            visibility="platform" if row["source"] == "SYSTEM" else "private", parent_id=None
        )
    insert_rows(conn, "exercises", exercises)
    insert_rows(conn, "exercise_muscles", rows(conn, legacy, "exercise_muscles"))
    profiles = rows(conn, legacy, "fitness_profiles")
    for row in profiles:
        row.update(
            days_per_week=3,
            session_minutes=45,
            available_equipment=["bodyweight"],
            preferred_discipline="strength",
        )
    insert_rows(conn, "fitness_profiles", profiles)
    for name in ("workouts", "splits", "training_plans"):
        data = rows(conn, legacy, name)
        for row in data:
            row.update(
                visibility="platform" if row["source"] == "SYSTEM" else "private",
                parent_id=None,
                is_active=True,
                created_at=now,
            )
            if name == "workouts":
                row["discipline"] = "strength"
            if name == "splits":
                split_days = [
                    day["order"]
                    for day in rows(conn, legacy, "split_days")
                    if day["split_id"] == row["id"]
                ]
                row["cycle_days"] = max([7, *split_days])
            if name == "training_plans":
                row["weeks"] = row.pop("duration_weeks") or 4
                row["goal"] = row["goal"] or "general_fitness"
        insert_rows(conn, name, data)
    data = rows(conn, legacy, "workout_exercises")
    for row in data:
        row["position"] = row.pop("order")
        row["weight_kg"] = row.pop("load_kg")
        row["progression"] = None
        Prescription.model_validate(
            {key: value for key, value in row.items() if key not in ("id", "workout_id")}
        )
    insert_rows(conn, "workout_exercises", data)
    days = rows(conn, legacy, "split_days")
    for row in days:
        row["day"] = row.pop("order")
        row["label"] = row.pop("name")
        SplitDayCreate.model_validate(
            {key: value for key, value in row.items() if key not in ("id", "split_id")}
        )
    insert_rows(conn, "split_days", days)
    # Only derive a calendar for a seven-day split. Longer cycles require review.
    schedules = []
    for plan in conn.execute(sa.select(Base.metadata.tables["training_plans"])).mappings():
        split = (
            conn.execute(
                sa.select(Base.metadata.tables["splits"]).where(
                    Base.metadata.tables["splits"].c.id == plan["split_id"]
                )
            )
            .mappings()
            .one()
        )
        if split["cycle_days"] == 7:
            for week in range(1, plan["weeks"] + 1):
                for day in days:
                    if day["split_id"] == plan["split_id"] and day["workout_id"] is not None:
                        if not 1 <= day["day"] <= 7:
                            raise ValueError("Split day outside 1..7; review the legacy plan")
                        schedules.append(
                            dict(
                                plan_id=plan["id"],
                                week=week,
                                day=day["day"],
                                workout_id=day["workout_id"],
                                phase=None,
                            )
                        )
    insert_rows(conn, "plan_days", schedules)
    insert_rows(conn, "training_sessions", rows(conn, legacy, "training_sessions"))
    counts = {}
    for name in (
        "users",
        "fitness_profiles",
        "exercises",
        "muscle_groups",
        "exercise_muscles",
        "workouts",
        "workout_exercises",
        "splits",
        "split_days",
        "training_plans",
        "training_sessions",
    ):
        original = conn.scalar(sa.select(sa.func.count()).select_from(legacy[name]))
        copied = conn.scalar(sa.select(sa.func.count()).select_from(Base.metadata.tables[name]))
        if original != copied:
            raise ValueError(f"Row-count mismatch in {name}: {original} != {copied}")
        counts[name] = copied
    return counts


def convert(database_engine, apply=False):
    if database_engine.dialect.name != "postgresql":
        raise ValueError("PC conversion requires PostgreSQL")
    archive = "kenfit_pc_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    with database_engine.connect() as conn:
        tx = conn.begin()
        try:
            conn.execute(sa.text("SELECT pg_advisory_xact_lock(742819)"))
            conn.execute(sa.text("SET LOCAL search_path TO public"))
            revisions = (
                conn.execute(sa.text("SELECT version_num FROM public.alembic_version"))
                .scalars()
                .all()
            )
            if revisions != [LEGACY_REVISION]:
                raise ValueError(f"Expected exactly {LEGACY_REVISION}; got {revisions}")
            legacy = sa.MetaData()
            legacy.reflect(conn, schema="public")
            # Lock all source tables; the API must be stopped during conversion.
            names = sorted(table.name for table in legacy.tables.values())
            expected = {
                "alembic_version",
                "users",
                "fitness_profiles",
                "exercises",
                "muscle_groups",
                "exercise_muscles",
                "workouts",
                "workout_exercises",
                "splits",
                "split_days",
                "training_plans",
                "training_sessions",
            }
            if set(names) != expected:
                raise ValueError(
                    f"Unexpected public schema; expected {sorted(expected)}, got {names}"
                )

            quoted = conn.dialect.identifier_preparer.quote
            for name in names:
                conn.execute(sa.text(f"LOCK TABLE public.{quoted(name)} IN ACCESS EXCLUSIVE MODE"))
            conn.execute(sa.text(f"CREATE SCHEMA {quoted(archive)}"))
            for name in names:
                conn.execute(
                    sa.text(f"ALTER TABLE public.{quoted(name)} SET SCHEMA {quoted(archive)}")
                )
            legacy = sa.MetaData()
            legacy.reflect(conn, schema=archive)
            legacy = {table.name: table for table in legacy.tables.values()}
            cfg = Config(str(Path(__file__).parents[1] / "alembic.ini"))
            cfg.attributes["connection"] = conn
            command.upgrade(cfg, "head")
            counts = transfer(conn, legacy)
            # Explicit IDs must not collide with the next generated ID.
            for table in Base.metadata.sorted_tables:
                if "id" in table.c and isinstance(table.c.id.type, sa.Integer):
                    sequence = conn.scalar(
                        sa.text("SELECT pg_get_serial_sequence(:table, 'id')"),
                        {"table": f"public.{table.name}"},
                    )
                    if sequence:
                        conn.execute(
                            sa.text(
                                "SELECT setval(CAST(:seq AS regclass), COALESCE((SELECT max(id) FROM "
                                + quoted(table.name)
                                + "), 1), EXISTS(SELECT 1 FROM "
                                + quoted(table.name)
                                + "))"
                            ),
                            {"seq": sequence},
                        )
            if apply:
                tx.commit()
            else:
                tx.rollback()
            return {
                "applied": apply,
                "archive_schema": archive if apply else None,
                "copied_rows": counts,
            }
        except BaseException:
            if tx.is_active:
                tx.rollback()
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="Commit; default is a dry run with rollback"
    )
    args = parser.parse_args()
    print(convert(engine, args.apply))


if __name__ == "__main__":
    main()
