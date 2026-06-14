-- ============================================================
-- Bible Schema — Phase 1
-- Public read-only reference data (no org_id / no tenant scope)
-- Deviation from multi-tenant rule: bible is global reference data
-- RLS: permissive SELECT for anon + authenticated; no writes via API
-- ============================================================

CREATE SCHEMA IF NOT EXISTS bible;

-- ── book ────────────────────────────────────────────────────
CREATE TABLE bible.book (
    id            SMALLINT PRIMARY KEY,          -- canonical book number 1-39 (Tanakh order)
    osis_id       TEXT        NOT NULL UNIQUE,   -- e.g. "Gen", "Exod"
    name_en       TEXT        NOT NULL,          -- "Genesis"
    name_he       TEXT        NOT NULL,          -- "בְּרֵאשִׁית"
    testament     TEXT        NOT NULL CHECK (testament IN ('torah','nevi_im','ketuvim')),
    book_order    SMALLINT    NOT NULL           -- display order within testament
);

-- ── chapter ─────────────────────────────────────────────────
CREATE TABLE bible.chapter (
    id            SERIAL      PRIMARY KEY,
    book_id       SMALLINT    NOT NULL REFERENCES bible.book(id),
    chapter_num   SMALLINT    NOT NULL,
    UNIQUE (book_id, chapter_num)
);

-- ── verse ────────────────────────────────────────────────────
CREATE TABLE bible.verse (
    id            SERIAL      PRIMARY KEY,
    chapter_id    INT         NOT NULL REFERENCES bible.chapter(id),
    verse_num     SMALLINT    NOT NULL,
    -- Convenience denorm for fast lookups
    book_id       SMALLINT    NOT NULL REFERENCES bible.book(id),
    chapter_num   SMALLINT    NOT NULL,
    UNIQUE (chapter_id, verse_num)
);

CREATE INDEX idx_verse_book_chapter ON bible.verse(book_id, chapter_num);

-- ── word ─────────────────────────────────────────────────────
CREATE TABLE bible.word (
    id            SERIAL      PRIMARY KEY,
    verse_id      INT         NOT NULL REFERENCES bible.verse(id),
    position      SMALLINT    NOT NULL,          -- 1-based word order within verse
    surface_he    TEXT        NOT NULL,          -- pointed Hebrew/Aramaic text
    display_he    TEXT,                          -- alternate display form (optional)
    lemma_strong  TEXT,                          -- Strong's number e.g. "H1234"
    morph_code    TEXT,                          -- raw OSHB morph string e.g. "HC/Td/Ncbsa"
    UNIQUE (verse_id, position)
);

CREATE INDEX idx_word_verse ON bible.word(verse_id);

-- ── morpheme ─────────────────────────────────────────────────
-- One row per morpheme segment within a word (split on '/')
CREATE TABLE bible.morpheme (
    id              SERIAL      PRIMARY KEY,
    word_id         INT         NOT NULL REFERENCES bible.word(id),
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

CREATE INDEX idx_morpheme_word ON bible.morpheme(word_id);

-- ── read views ───────────────────────────────────────────────
CREATE OR REPLACE VIEW bible.book_read       AS SELECT * FROM bible.book;
CREATE OR REPLACE VIEW bible.chapter_read    AS SELECT * FROM bible.chapter;
CREATE OR REPLACE VIEW bible.verse_read      AS SELECT * FROM bible.verse;
CREATE OR REPLACE VIEW bible.word_read       AS SELECT * FROM bible.word;
CREATE OR REPLACE VIEW bible.morpheme_read   AS SELECT * FROM bible.morpheme;

-- ── RLS ──────────────────────────────────────────────────────
-- Bible is global reference data — public read (anon + authenticated)
-- No writes via RLS (import pipeline uses service role)

ALTER TABLE bible.book      ENABLE ROW LEVEL SECURITY;
ALTER TABLE bible.chapter   ENABLE ROW LEVEL SECURITY;
ALTER TABLE bible.verse     ENABLE ROW LEVEL SECURITY;
ALTER TABLE bible.word      ENABLE ROW LEVEL SECURITY;
ALTER TABLE bible.morpheme  ENABLE ROW LEVEL SECURITY;

-- Public SELECT for anon role
CREATE POLICY "bible.book: public read"
    ON bible.book FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "bible.chapter: public read"
    ON bible.chapter FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "bible.verse: public read"
    ON bible.verse FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "bible.word: public read"
    ON bible.word FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "bible.morpheme: public read"
    ON bible.morpheme FOR SELECT TO anon, authenticated USING (true);
