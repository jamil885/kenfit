from pathlib import Path

from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from alembic import command


def test_upgrade_preserves_legacy_data_and_downgrade(tmp_path):
    url = "sqlite:///" + str(tmp_path / "legacy.db")
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    config.attributes["database_url"] = url
    command.upgrade(config, "cc8be0ff1fcf")
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO users (id,name,email,password_hash,is_active) VALUES (1,'Legacy','legacy@example.com','placeholder',1)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO fitness_profiles (id,user_id,birth_date,gender,height_cm,weight_kg,fitness_level,goal) VALUES (1,1,'2000-01-01','male',175,75,'beginner','general_fitness')"
            )
        )
        conn.execute(
            text(
                "INSERT INTO exercises (id,name,discipline,exercise_type,is_active,created_at) VALUES (1,'Legacy drill','sport_custom','drill',1,'2026-01-01')"
            )
        )
        conn.execute(text("INSERT INTO muscle_groups (id,name) VALUES (1,'core')"))
        conn.execute(
            text(
                "INSERT INTO exercise_muscles (id,exercise_id,muscle_group_id,role) VALUES (1,1,1,'primary')"
            )
        )
    command.upgrade(config, "head")
    with engine.connect() as conn:
        assert conn.execute(text("SELECT name FROM users WHERE id=1")).scalar() == "Legacy"
        assert conn.execute(text("SELECT source FROM exercises WHERE id=1")).scalar() == "SYSTEM"
        assert conn.execute(text("SELECT code FROM disciplines")).scalar() == "sport_custom"
        assert (
            conn.execute(text("SELECT days_per_week FROM fitness_profiles WHERE id=1")).scalar()
            == 3
        )
        assert conn.execute(text("SELECT COUNT(*) FROM exercise_muscles")).scalar() == 1
        assert conn.execute(text("PRAGMA foreign_key_check")).all() == []
    command.check(config)
    command.downgrade(config, "cc8be0ff1fcf")
    assert "workouts" not in inspect(engine).get_table_names()
    with engine.connect() as conn:
        assert (
            conn.execute(text("SELECT name FROM exercises WHERE id=1")).scalar() == "Legacy drill"
        )
    engine.dispose()
