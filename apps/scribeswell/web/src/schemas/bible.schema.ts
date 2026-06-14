/**
 * Bible Zod schemas — silo-local copy.
 *
 * Per silo rules: schemas live in apps/<app>/web/src/schemas/ (not platform/shared).
 * These mirror the Pydantic models in apps/scribeswell/backend/schemas/.
 *
 * Previously imported from @platform/shared/schemas/zod/bible/bible.schema —
 * migrated to silo-local in Phase 2 (tsc clean-up).
 */
import { z } from "zod";

// ── Book ──────────────────────────────────────────────────────────────────────

export const BookResponseSchema = z.object({
  osis_id: z.string(),
  name_en: z.string(),
  name_he: z.string(),
  testament: z.string(),
  chapter_count: z.number().int(),
});

export type BookResponse = z.infer<typeof BookResponseSchema>;

export const BooksListResponseSchema = z.object({
  books: z.array(BookResponseSchema),
});

export type BooksListResponse = z.infer<typeof BooksListResponseSchema>;

// ── Chapter ───────────────────────────────────────────────────────────────────

export const ChapterSummarySchema = z.object({
  id: z.number().int(),
  chapter_num: z.number().int(),
  verse_count: z.number().int(),
});

export type ChapterSummary = z.infer<typeof ChapterSummarySchema>;

export const BookWithChaptersResponseSchema = z.object({
  book: BookResponseSchema,
  chapters: z.array(ChapterSummarySchema),
  name_en: z.string().optional(),  // convenience alias used in ReaderPage
});

export type BookWithChaptersResponse = z.infer<typeof BookWithChaptersResponseSchema>;

// ── Word ──────────────────────────────────────────────────────────────────────

export const WordResponseSchema = z.object({
  id: z.number().int(),
  surface_he: z.string(),
  lemma_strong: z.string().nullable(),
  word_order: z.number().int(),
});

export type WordResponse = z.infer<typeof WordResponseSchema>;

// ── Verse ─────────────────────────────────────────────────────────────────────

export const VerseWithWordsResponseSchema = z.object({
  id: z.number().int(),
  verse_num: z.number().int(),
  words: z.array(WordResponseSchema),
});

export type VerseWithWordsResponse = z.infer<typeof VerseWithWordsResponseSchema>;

export const VersesListResponseSchema = z.object({
  verses: z.array(VerseWithWordsResponseSchema),
});

export type VersesListResponse = z.infer<typeof VersesListResponseSchema>;

export const ChapterWithVersesResponseSchema = z.object({
  book_osis_id: z.string(),
  chapter_num: z.number().int(),
  verses: z.array(VerseWithWordsResponseSchema),
});

export type ChapterWithVersesResponse = z.infer<typeof ChapterWithVersesResponseSchema>;

// ── Morphology ────────────────────────────────────────────────────────────────

export const MorphemeSchema = z.object({
  segment_index: z.number().int(),
  pos_code: z.string().nullable(),
  part_of_speech: z.string().nullable(),
  language: z.string().nullable(),
  verb_stem: z.string().nullable(),
  verb_aspect: z.string().nullable(),
  person: z.string().nullable(),
  gender: z.string().nullable(),
  number: z.string().nullable(),
  state: z.string().nullable(),
});

export type Morpheme = z.infer<typeof MorphemeSchema>;

export const WordWithMorphologyResponseSchema = z.object({
  surface_he: z.string(),
  lemma_strong: z.string().nullable(),
  morph_code: z.string().nullable(),
  morphemes: z.array(MorphemeSchema),
});

export type WordWithMorphologyResponse = z.infer<typeof WordWithMorphologyResponseSchema>;
