-- ============================================================
-- Bible Schema — Phase 1
-- Public read-only reference data (no org_id / no tenant scope)
-- Deviation from multi-tenant rule: bible is global reference data
-- RLS: permissive SELECT for anon + authenticated; no writes via API
-- ============================================================

CREATE SCHEMA IF NOT EXISTS scribeswell;

-- ── book ────────────────────────────────────────────────────
CREATE TABLE scribeswell.book (
    id            SMALLINT PRIMARY KEY,          -- canonical book number 1-39 (Tanakh order)
    osis_id       TEXT        NOT NULL UNIQUE,   -- e.g. "Gen", "Exod"
    name_en       TEXT        NOT NULL,          -- "Genesis"
    name_he       TEXT        NOT NULL,          -- "בְּרֵאשִׁית"
    testament     TEXT        NOT NULL CHECK (testament IN ('torah','nevi_im','ketuvim')),
    book_order    SMALLINT    NOT NULL           -- display order within testament
);

-- ── chapter ─────────────────────────────────────────────────
CREATE TABLE scribeswell.chapter (
    id            SERIAL      PRIMARY KEY,
    book_id       SMALLINT    NOT NULL REFERENCES scribeswell.book(id),
    chapter_num   SMALLINT    NOT NULL,
    UNIQUE (book_id, chapter_num)
);

-- ── verse ────────────────────────────────────────────────────
CREATE TABLE scribeswell.verse (
    id            SERIAL      PRIMARY KEY,
    chapter_id    INT         NOT NULL REFERENCES scribeswell.chapter(id),
    verse_num     SMALLINT    NOT NULL,
    -- Convenience denorm for fast lookups
    book_id       SMALLINT    NOT NULL REFERENCES scribeswell.book(id),
    chapter_num   SMALLINT    NOT NULL,
    UNIQUE (chapter_id, verse_num)
);

CREATE INDEX idx_verse_book_chapter ON scribeswell.verse(book_id, chapter_num);

-- ── word ─────────────────────────────────────────────────────
CREATE TABLE scribeswell.word (
    id            SERIAL      PRIMARY KEY,
    verse_id      INT         NOT NULL REFERENCES scribeswell.verse(id),
    position      SMALLINT    NOT NULL,          -- 1-based word order within verse
    surface_he    TEXT        NOT NULL,          -- pointed Hebrew/Aramaic text
    display_he    TEXT,                          -- alternate display form (optional)
    lemma_strong  TEXT,                          -- Strong's number e.g. "H1234"
    morph_code    TEXT,                          -- raw OSHB morph string e.g. "HC/Td/Ncbsa"
    UNIQUE (verse_id, position)
);

CREATE INDEX idx_word_verse ON scribeswell.word(verse_id);

-- ── morpheme ─────────────────────────────────────────────────
-- One row per morpheme segment within a word (split on '/')
CREATE TABLE scribeswell.morpheme (
    id              SERIAL      PRIMARY KEY,
    word_id         INT         NOT NULL REFERENCES scribeswell.word(id),
    segment_index   SMALLINT    NOT NULL,        -- 0-based position in morph_code split
    language        TEXT        NOT NULL CHECK (language IN ('hebrew','aramaic')),
    part_of_speech  TEXT        NOT NULL,        -- decoded: noun/verb/adjective/preposition/...
    pos_code        TEXT        NOT NULL,        -- raw segment e.g. "Ncbsa", "Vqp3ms"
    -- Nominal features (nullable)
    gender          TEXT        CHECK (gender IN ('masculine','feminine','both','common','unknown')),
    number          TEXT        CHECK (number IN ('singular','plural','dual','unknown')),
    state           TEXT        CHECK (state IN ('absolute','construct','determined','unknown')),
    -- Verbal features (nullable)
    verb_stem       TEXT,                        -- qal/niphal/piel/pual/hiphil/hophal/hithpael/...
    verb_aspect     TEXT,                        -- perfect/imperfect/imperative/infinitive_construct/...
    person          TEXT        CHECK (person IN ('first','second','third','unknown')),
    UNIQUE (word_id, segment_index)
);

CREATE INDEX idx_morpheme_word ON scribeswell.morpheme(word_id);

-- ── read views ───────────────────────────────────────────────
CREATE OR REPLACE VIEW scribeswell.book_read       AS SELECT * FROM scribeswell.book;
CREATE OR REPLACE VIEW scribeswell.chapter_read    AS SELECT * FROM scribeswell.chapter;
CREATE OR REPLACE VIEW scribeswell.verse_read      AS SELECT * FROM scribeswell.verse;
CREATE OR REPLACE VIEW scribeswell.word_read       AS SELECT * FROM scribeswell.word;
CREATE OR REPLACE VIEW scribeswell.morpheme_read   AS SELECT * FROM scribeswell.morpheme;

-- ── RLS ──────────────────────────────────────────────────────
-- Bible is global reference data — public read (anon + authenticated)
-- No writes via RLS (import pipeline uses service role)

ALTER TABLE scribeswell.book      ENABLE ROW LEVEL SECURITY;
ALTER TABLE scribeswell.chapter   ENABLE ROW LEVEL SECURITY;
ALTER TABLE scribeswell.verse     ENABLE ROW LEVEL SECURITY;
ALTER TABLE scribeswell.word      ENABLE ROW LEVEL SECURITY;
ALTER TABLE scribeswell.morpheme  ENABLE ROW LEVEL SECURITY;

-- Public SELECT for anon role
CREATE POLICY "scribeswell.book: public read"
    ON scribeswell.book FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "scribeswell.chapter: public read"
    ON scribeswell.chapter FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "scribeswell.verse: public read"
    ON scribeswell.verse FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "scribeswell.word: public read"
    ON scribeswell.word FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "scribeswell.morpheme: public read"
    ON scribeswell.morpheme FOR SELECT TO anon, authenticated USING (true);


-- Grants to the anon role
grant usage on schema scribeswell to anon;
GRANT SELECT ON book IN SCHEMA scribeswell TO service_role;
GRANT SELECT ON chapter IN SCHEMA scribeswell TO service_role;
GRANT SELECT ON verse IN SCHEMA scribeswell TO service_role;
GRANT SELECT ON word IN SCHEMA scribeswell TO service_role;
GRANT SELECT ON morpheme IN SCHEMA scribeswell TO service_role;

-- Grants to the service role
GRANT USAGE ON SCHEMA scribeswell TO service_role;  -- equivalent elevated role
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA scribeswell TO service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA scribeswell
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO service_role;

-- Grants to authenticated users (RLS policies control actual access)
-- Note: SELECT permission on views only (granted above for users_read)
GRANT USAGE ON SCHEMA scribeswell TO authenticated;
GRANT INSERT, UPDATE ON ALL TABLES IN SCHEMA scribeswell TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA scribeswell
  GRANT INSERT, UPDATE ON TABLES TO authenticated;