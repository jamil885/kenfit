"""Exercise real PostgreSQL DDL, archives, rollback and data conversion in CI."""

from pathlib import Path

import pytest
import sqlalchemy as sa

from app.core.database import Base, engine
from app.migrate_pc import convert


def legacy_database():
    Base.metadata.drop_all(engine)
    with engine.begin() as conn:
        conn.execute(sa.text("DROP TABLE alembic_version"))
        sql = (Path(__file__).parent / "fixtures/pc_schema.sql").read_text()
        for statement in sql.split(";"):
            if statement.strip() in ("BEGIN", "COMMIT") or not statement.strip():
                continue
            conn.exec_driver_sql(statement)
        conn.execute(
            sa.text(
                "INSERT INTO users VALUES (10, 'PC User', 'pc@example.com', 'retained-hash', true)"
            )
        )
        conn.execute(
            sa.text(
                "INSERT INTO fitness_profiles (id,user_id,birth_date,gender,height_cm,weight_kg,fitness_level,goal) VALUES (10,10,'2000-01-01','male',175,75,'beginner','general_fitness')"
            )
        )
        conn.execute(
            sa.text(
                "INSERT INTO exercises (id,name,discipline,exercise_type,is_active,created_at,owner_id,source) VALUES (10,'PC Squat','strength','strength',true,'2026-01-01',10,'USER')"
            )
        )
        conn.execute(sa.text("INSERT INTO muscle_groups VALUES (10,'Legs')"))
        conn.execute(sa.text("INSERT INTO exercise_muscles VALUES (10,10,10,'primary')"))
        conn.execute(
            sa.text("INSERT INTO workouts VALUES (10,'PC Workout','Original notes',10,'USER')")
        )
        conn.execute(
            sa.text(
                "INSERT INTO workout_exercises (id,workout_id,exercise_id,\"order\",sets,reps,load_kg,notes) VALUES (10,10,10,1,3,8,25,'Keep notes')"
            )
        )
        conn.execute(sa.text("INSERT INTO splits VALUES (10,'PC Split',NULL,10,'USER')"))
        conn.execute(sa.text("INSERT INTO split_days VALUES (10,10,10,1,'Day one')"))
        conn.execute(
            sa.text(
                "INSERT INTO training_plans VALUES (10,'PC Plan',NULL,'general_fitness',4,10,10,'USER')"
            )
        )
        conn.execute(
            sa.text(
                "INSERT INTO training_sessions VALUES (10,10,10,10,'2026-01-01 10:00+00','2026-01-01 11:00+00','COMPLETED','Historic session')"
            )
        )


@pytest.mark.skipif(
    engine.dialect.name != "postgresql", reason="Requires dedicated PostgreSQL CI database"
)
def test_pc_conversion_dry_run_commit_and_sequences():
    legacy_database()
    report = convert(engine, apply=False)
    assert report["applied"] is False
    with engine.connect() as conn:
        assert conn.scalar(sa.text("SELECT version_num FROM alembic_version")) == "fea8b9182489"
        assert (
            conn.scalar(
                sa.text("SELECT count(*) FROM pg_namespace WHERE nspname LIKE 'kenfit_pc_%'")
            )
            == 0
        )
    report = convert(engine, apply=True)
    archive = report["archive_schema"]
    try:
        with engine.begin() as conn:
            assert conn.scalar(sa.text("SELECT version_num FROM alembic_version")) == "9c4a10b2d7ef"
            assert (
                conn.scalar(sa.text("SELECT password_hash FROM users WHERE id=10"))
                == "retained-hash"
            )
            assert conn.scalar(sa.text("SELECT weight_kg FROM workout_exercises WHERE id=10")) == 25
            assert (
                conn.scalar(sa.text("SELECT notes FROM training_sessions WHERE id=10"))
                == "Historic session"
            )
            assert conn.scalar(sa.text("SELECT count(*) FROM plan_days")) == 4
            assert (
                conn.scalar(sa.text(f'SELECT version_num FROM "{archive}".alembic_version'))
                == "fea8b9182489"
            )
            assert (
                conn.scalar(
                    sa.text(
                        "INSERT INTO users (name,email,password_hash,is_active) VALUES ('New','new@example.com','hash',true) RETURNING id"
                    )
                )
                > 10
            )
        with pytest.raises(ValueError, match="Expected exactly"):
            convert(engine, apply=True)
    finally:
        with engine.begin() as conn:
            conn.execute(sa.text(f'DROP SCHEMA "{archive}" CASCADE'))


@pytest.mark.skipif(
    engine.dialect.name != "postgresql", reason="Requires dedicated PostgreSQL CI database"
)
def test_pc_conversion_failure_rolls_back_schema_and_rows():
    legacy_database()
    with engine.begin() as conn:
        # Local names allowed 120 chars; MVP allows 100. Never silently truncate.
        conn.execute(sa.text("UPDATE workouts SET name=:name"), {"name": "x" * 110})
    with pytest.raises(sa.exc.DataError):
        convert(engine, apply=True)
    with engine.connect() as conn:
        assert conn.scalar(sa.text("SELECT version_num FROM alembic_version")) == "fea8b9182489"
        assert conn.scalar(sa.text("SELECT name FROM workouts WHERE id=10")) == "x" * 110
        assert (
            conn.scalar(
                sa.text("SELECT count(*) FROM pg_namespace WHERE nspname LIKE 'kenfit_pc_%'")
            )
            == 0
        )
    # Restore current schema for subsequent test fixtures.
    with engine.begin() as conn:
        conn.execute(sa.text("UPDATE workouts SET name='PC Workout'"))
    report = convert(engine, apply=True)
    with engine.begin() as conn:
        conn.execute(sa.text(f'DROP SCHEMA "{report["archive_schema"]}" CASCADE'))
