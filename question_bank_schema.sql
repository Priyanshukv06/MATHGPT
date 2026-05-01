CREATE TABLE IF NOT EXISTS question_bank (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    topic       TEXT        NOT NULL,
    difficulty  TEXT        NOT NULL,
    question    TEXT        NOT NULL,
    solution    TEXT,
    source      TEXT,
    tags        TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);
ALTER TABLE question_bank DISABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_qb_topic      ON question_bank(topic);
CREATE INDEX IF NOT EXISTS idx_qb_difficulty ON question_bank(difficulty);