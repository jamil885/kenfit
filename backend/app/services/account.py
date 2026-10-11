import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.account import AuthRateLimit, PasswordReset
from app.models.user import User
from app.services.auth import hash_password, verify_password
from app.services.mail import clear_local_mail, deliver

GENERIC = "If the account exists, you will receive recovery instructions."


def now():
    return datetime.now(timezone.utc)


def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


def rate_limit(db, scope, subject, maximum):
    current = now()
    window = int(current.timestamp()) // 3600
    key = hmac.new(
        settings.jwt_secret_key.encode(), f"{scope}:{subject}:{window}".encode(), hashlib.sha256
    ).hexdigest()
    db.execute(sa.delete(AuthRateLimit).where(AuthRateLimit.expires_at < current))
    insert = pg_insert if db.bind.dialect.name == "postgresql" else sqlite_insert
    stmt = insert(AuthRateLimit).values(key=key, count=1, expires_at=current + timedelta(hours=1))
    stmt = stmt.on_conflict_do_update(
        index_elements=["key"], set_={"count": AuthRateLimit.count + 1}
    ).returning(AuthRateLimit.count)
    count = db.scalar(stmt)
    db.commit()
    return count <= maximum


def request_reset(db, email, tasks):
    if settings.mail_mode == "disabled":
        raise HTTPException(503, "Password recovery is not configured")
    allowed = rate_limit(db, "recovery-email", email.lower(), 3)
    token = secrets.token_urlsafe(32)
    user = db.scalar(
        sa.select(User).where(sa.func.lower(User.email) == email.lower(), User.is_active.is_(True))
    )
    # Query and generate randomness for both known and unknown emails. Delivery runs after response.
    if user is not None and allowed:
        db.execute(sa.delete(PasswordReset).where(PasswordReset.expires_at < now()))
        db.add(
            PasswordReset(
                token_hash=digest(token), user_id=user.id, expires_at=now() + timedelta(minutes=15)
            )
        )
        db.commit()
        tasks.add_task(
            deliver,
            user.email,
            "Recupera tu contraseña de KenFit",
            f"En KenFit abre Recuperar contraseña y pega este código:\n\n{token}\n\nVence en 15 minutos y sirve una sola vez. Si no lo solicitaste, ignora este mensaje.",
        )
    return {"message": GENERIC}


def reset_password(db, token, password, tasks):
    # DELETE RETURNING atomically consumes the token; rollback restores it on failure.
    user_id = db.scalar(
        sa.delete(PasswordReset)
        .where(PasswordReset.token_hash == digest(token), PasswordReset.expires_at > now())
        .returning(PasswordReset.user_id)
    )
    user = (
        db.scalar(
            sa.select(User).where(User.id == user_id, User.is_active.is_(True)).with_for_update()
        )
        if user_id is not None
        else None
    )
    if user is None:
        db.rollback()
        raise HTTPException(400, "Invalid or expired recovery code")
    user.password_hash = hash_password(password)
    user.token_version += 1
    db.execute(sa.delete(PasswordReset).where(PasswordReset.user_id == user.id))
    db.commit()
    tasks.add_task(
        deliver,
        user.email,
        "Tu contraseña de KenFit cambió",
        "Tu contraseña fue actualizada. Se cerraron las sesiones anteriores. Si no reconoces el cambio, solicita recuperación y contacta con soporte.",
    )
    return {"message": "Password updated. Sign in again."}


def erase_schema(conn, schema, email):
    metadata = sa.MetaData()
    metadata.reflect(conn, schema=schema)
    tables = {table.name: table for table in metadata.tables.values()}
    if "users" not in tables:
        raise ValueError("Account archive has no users table")
    user_id = conn.scalar(
        sa.select(tables["users"].c.id).where(
            sa.func.lower(tables["users"].c.email) == email.lower()
        )
    )
    if user_id is None:
        return
    owned = {}
    for name in ("exercises", "workouts", "splits", "training_plans", "foods"):
        if name in tables:
            table = tables[name]
            owned[name] = list(
                conn.scalars(sa.select(table.c.id).where(table.c.owner_id == user_id))
            )
            if "parent_id" in table.c:
                conn.execute(
                    table.update().where(table.c.parent_id.in_(owned[name])).values(parent_id=None)
                )
    logs = []
    if "workout_logs" in tables:
        logs = list(
            conn.scalars(
                sa.select(tables["workout_logs"].c.id).where(
                    tables["workout_logs"].c.user_id == user_id
                )
            )
        )
    for name, field, ids in (
        ("set_results", "log_id", logs),
        ("plan_days", "plan_id", owned.get("training_plans", [])),
        ("split_days", "split_id", owned.get("splits", [])),
        ("workout_exercises", "workout_id", owned.get("workouts", [])),
        ("exercise_muscles", "exercise_id", owned.get("exercises", [])),
    ):
        if name in tables:
            conn.execute(tables[name].delete().where(tables[name].c[field].in_(ids)))
    # Nullable references can retain another person's independent session or rest day.
    if "split_days" in tables:
        conn.execute(
            tables["split_days"]
            .update()
            .where(tables["split_days"].c.workout_id.in_(owned.get("workouts", [])))
            .values(workout_id=None)
        )
    if "training_sessions" in tables:
        for field, source in (("workout_id", "workouts"), ("training_plan_id", "training_plans")):
            conn.execute(
                tables["training_sessions"]
                .update()
                .where(tables["training_sessions"].c[field].in_(owned.get(source, [])))
                .values(**{field: None})
            )
    for name in (
        "set_results",
        "password_resets",
        "meal_entries",
        "nutrition_targets",
        "weight_entries",
        "training_sessions",
        "workout_logs",
        "fitness_profiles",
    ):
        if name in tables and "user_id" in tables[name].c:
            conn.execute(tables[name].delete().where(tables[name].c.user_id == user_id))
    for name in ("training_plans", "splits", "workouts", "exercises", "foods"):
        if name in tables:
            conn.execute(tables[name].delete().where(tables[name].c.owner_id == user_id))
    conn.execute(tables["users"].delete().where(tables["users"].c.id == user_id))


def delete_account(db: Session, user, password):
    # Lock the account so reset/delete cannot race against one another.
    locked = db.scalar(
        sa.select(User)
        .where(User.id == user.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if locked is None or not locked.is_active:
        raise HTTPException(401, "Invalid credentials")
    if not verify_password(password, locked.password_hash):
        raise HTTPException(400, "Incorrect current password")
    email = locked.email
    conn = db.connection()
    if conn.dialect.name == "postgresql":
        schemas = [
            name for name in sa.inspect(conn).get_schema_names() if name.startswith("kenfit_pc_")
        ]
        for schema in schemas:
            erase_schema(conn, schema, email)
        erase_schema(conn, "public", email)
    else:
        erase_schema(conn, None, email)
    db.commit()

    clear_local_mail(email)
