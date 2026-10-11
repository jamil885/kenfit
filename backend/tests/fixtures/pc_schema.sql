BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 49e18fd1d91f

CREATE TABLE users (
    id SERIAL NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    email VARCHAR(255) NOT NULL, 
    password_hash VARCHAR(255) NOT NULL, 
    is_active BOOLEAN NOT NULL, 
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE INDEX ix_users_id ON users (id);

INSERT INTO alembic_version (version_num) VALUES ('49e18fd1d91f') RETURNING alembic_version.version_num;

-- Running upgrade 49e18fd1d91f -> 5052fc0477a4

CREATE TABLE fitness_profiles (
    id SERIAL NOT NULL, 
    user_id INTEGER NOT NULL, 
    birth_date DATE NOT NULL, 
    gender VARCHAR(50) NOT NULL, 
    height_cm FLOAT NOT NULL, 
    weight_kg FLOAT NOT NULL, 
    fitness_level VARCHAR(30) NOT NULL, 
    goal VARCHAR(50) NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_fitness_profiles_id ON fitness_profiles (id);

CREATE UNIQUE INDEX ix_fitness_profiles_user_id ON fitness_profiles (user_id);

UPDATE alembic_version SET version_num='5052fc0477a4' WHERE alembic_version.version_num = '49e18fd1d91f';

-- Running upgrade 5052fc0477a4 -> cc8be0ff1fcf

CREATE TABLE exercises (
    id SERIAL NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    description TEXT, 
    discipline VARCHAR(50) NOT NULL, 
    modality VARCHAR(50), 
    exercise_type VARCHAR(50) NOT NULL, 
    equipment VARCHAR(100), 
    difficulty VARCHAR(30), 
    instructions TEXT, 
    is_active BOOLEAN NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_exercises_id ON exercises (id);

CREATE TABLE muscle_groups (
    id SERIAL NOT NULL, 
    name VARCHAR(50) NOT NULL, 
    description VARCHAR(255), 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

CREATE INDEX ix_muscle_groups_id ON muscle_groups (id);

CREATE TABLE exercise_muscles (
    id SERIAL NOT NULL, 
    exercise_id INTEGER NOT NULL, 
    muscle_group_id INTEGER NOT NULL, 
    role VARCHAR(20) NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(exercise_id) REFERENCES exercises (id) ON DELETE CASCADE, 
    FOREIGN KEY(muscle_group_id) REFERENCES muscle_groups (id) ON DELETE CASCADE
);

CREATE INDEX ix_exercise_muscles_exercise_id ON exercise_muscles (exercise_id);

CREATE INDEX ix_exercise_muscles_id ON exercise_muscles (id);

CREATE INDEX ix_exercise_muscles_muscle_group_id ON exercise_muscles (muscle_group_id);

UPDATE alembic_version SET version_num='cc8be0ff1fcf' WHERE alembic_version.version_num = '5052fc0477a4';

-- Running upgrade cc8be0ff1fcf -> a0b407008d13

CREATE TABLE workouts (
    id SERIAL NOT NULL, 
    name VARCHAR(120) NOT NULL, 
    description TEXT, 
    owner_id INTEGER, 
    source VARCHAR(20) NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_workouts_id ON workouts (id);

CREATE INDEX ix_workouts_owner_id ON workouts (owner_id);

UPDATE alembic_version SET version_num='a0b407008d13' WHERE alembic_version.version_num = 'cc8be0ff1fcf';

-- Running upgrade a0b407008d13 -> dac4af7ed78c

CREATE TABLE workout_exercises (
    id SERIAL NOT NULL, 
    workout_id INTEGER NOT NULL, 
    exercise_id INTEGER NOT NULL, 
    "order" INTEGER NOT NULL, 
    sets INTEGER, 
    reps INTEGER, 
    duration_seconds INTEGER, 
    distance_meters FLOAT, 
    load_kg FLOAT, 
    intensity VARCHAR(50), 
    rest_seconds INTEGER, 
    tempo VARCHAR(30), 
    notes TEXT, 
    PRIMARY KEY (id), 
    FOREIGN KEY(exercise_id) REFERENCES exercises (id) ON DELETE CASCADE, 
    FOREIGN KEY(workout_id) REFERENCES workouts (id) ON DELETE CASCADE
);

CREATE INDEX ix_workout_exercises_exercise_id ON workout_exercises (exercise_id);

CREATE INDEX ix_workout_exercises_id ON workout_exercises (id);

CREATE INDEX ix_workout_exercises_workout_id ON workout_exercises (workout_id);

UPDATE alembic_version SET version_num='dac4af7ed78c' WHERE alembic_version.version_num = 'a0b407008d13';

-- Running upgrade dac4af7ed78c -> bf389238eaa3

ALTER TABLE exercises ADD COLUMN owner_id INTEGER;

ALTER TABLE exercises ADD COLUMN source VARCHAR(20);

UPDATE exercises SET source = 'SYSTEM' WHERE source IS NULL;

ALTER TABLE exercises ALTER COLUMN source SET NOT NULL;

CREATE INDEX ix_exercises_owner_id ON exercises (owner_id);

ALTER TABLE exercises ADD CONSTRAINT fk_exercises_owner_id_users FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE CASCADE;

UPDATE alembic_version SET version_num='bf389238eaa3' WHERE alembic_version.version_num = 'dac4af7ed78c';

-- Running upgrade bf389238eaa3 -> f834e1d6a96e

CREATE TABLE splits (
    id SERIAL NOT NULL, 
    name VARCHAR(120) NOT NULL, 
    description TEXT, 
    owner_id INTEGER, 
    source VARCHAR(20) NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_splits_id ON splits (id);

CREATE INDEX ix_splits_owner_id ON splits (owner_id);

CREATE TABLE split_days (
    id SERIAL NOT NULL, 
    split_id INTEGER NOT NULL, 
    workout_id INTEGER, 
    "order" INTEGER NOT NULL, 
    name VARCHAR(100), 
    PRIMARY KEY (id), 
    FOREIGN KEY(split_id) REFERENCES splits (id) ON DELETE CASCADE, 
    FOREIGN KEY(workout_id) REFERENCES workouts (id) ON DELETE SET NULL
);

CREATE INDEX ix_split_days_id ON split_days (id);

CREATE INDEX ix_split_days_split_id ON split_days (split_id);

CREATE INDEX ix_split_days_workout_id ON split_days (workout_id);

UPDATE alembic_version SET version_num='f834e1d6a96e' WHERE alembic_version.version_num = 'bf389238eaa3';

-- Running upgrade f834e1d6a96e -> 5a3328c803bd

CREATE TABLE training_plans (
    id SERIAL NOT NULL, 
    name VARCHAR(120) NOT NULL, 
    description TEXT, 
    goal VARCHAR(100), 
    duration_weeks INTEGER, 
    split_id INTEGER NOT NULL, 
    owner_id INTEGER, 
    source VARCHAR(20) NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE CASCADE, 
    FOREIGN KEY(split_id) REFERENCES splits (id) ON DELETE RESTRICT
);

CREATE INDEX ix_training_plans_id ON training_plans (id);

CREATE INDEX ix_training_plans_owner_id ON training_plans (owner_id);

CREATE INDEX ix_training_plans_split_id ON training_plans (split_id);

UPDATE alembic_version SET version_num='5a3328c803bd' WHERE alembic_version.version_num = 'f834e1d6a96e';

-- Running upgrade 5a3328c803bd -> fea8b9182489

CREATE TABLE training_sessions (
    id SERIAL NOT NULL, 
    user_id INTEGER NOT NULL, 
    workout_id INTEGER, 
    training_plan_id INTEGER, 
    started_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    finished_at TIMESTAMP WITH TIME ZONE, 
    status VARCHAR(20) NOT NULL, 
    notes TEXT, 
    PRIMARY KEY (id), 
    FOREIGN KEY(training_plan_id) REFERENCES training_plans (id) ON DELETE SET NULL, 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
    FOREIGN KEY(workout_id) REFERENCES workouts (id) ON DELETE SET NULL
);

CREATE INDEX ix_training_sessions_id ON training_sessions (id);

CREATE INDEX ix_training_sessions_training_plan_id ON training_sessions (training_plan_id);

CREATE INDEX ix_training_sessions_user_id ON training_sessions (user_id);

CREATE INDEX ix_training_sessions_workout_id ON training_sessions (workout_id);

UPDATE alembic_version SET version_num='fea8b9182489' WHERE alembic_version.version_num = '5a3328c803bd';

COMMIT;

