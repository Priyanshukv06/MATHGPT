CREATE TABLE IF NOT EXISTS chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL, role TEXT NOT NULL,
    content TEXT, model TEXT, created_at TIMESTAMPTZ DEFAULT now()
);
ALTER TABLE chat_history DISABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS practice_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL, topic TEXT, difficulty TEXT,
    question TEXT, user_answer TEXT, score SMALLINT,
    created_at TIMESTAMPTZ DEFAULT now()
);
ALTER TABLE practice_sessions DISABLE ROW LEVEL SECURITY;