/**
 * Bible Zod schemas — silo-local copy.
 *
 * Per silo rules: schemas live in apps/<app>/web/src/schemas/ (not platform/shared).
 * These mirror the Pydantic models in apps/scribeswell/backend/schemas/.
 */
import { z } from "zod";

// ── Book ──────────────────────────────────────────────────────────────────────

export const BookResponseSchema = z.object({
  id: z.number().int(),
  osis_id: z.string(),
  name_en: z.string(),
  name_he: z.string(),
  testament: z.string(),
  // division is present in the Pydantic schema but not always populated from DB;
  // make optional so Zod does not reject responses where it is absent.
  division: z.string().optional(),
  book_order: z.number().int(),
});

export type BookResponse = z.infer<typeof BookResponseSchema>;

export const BooksListResponseSchema = z.object({
  data: z.array(BookResponseSchema),
  total: z.number().int(),
});

export type BooksListResponse = z.infer<typeof BooksListResponseSchema>;

// ── Chapter ───────────────────────────────────────────────────────────────────

export const ChapterSummarySchema = z.object({
  id: z.number().int(),
  chapter_num: z.number().int(),
});

export type ChapterSummary = z.infer<typeof ChapterSummarySchema>;

export const BookWithChaptersResponseSchema = BookResponseSchema.extend({
  chapters: z.array(ChapterSummarySchema),
});

export type BookWithChaptersResponse = z.infer<typeof BookWithChaptersResponseSchema>;

// ── Verse / Word ──────────────────────────────────────────────────────────────

export const WordResponseSchema = z.object({
  id: z.number().int(),
  position: z.number().int(),
  surface_he: z.string(),
  display_he: z.string().nullable(),
  lemma_strong: z.string().nullable(),
  morph_code: z.string().nullable(),
});

export type WordResponse = z.infer<typeof WordResponseSchema>;

export const VerseSummarySchema = z.object({
  id: z.number().int(),
  verse_num: z.number().int(),
});

export type VerseSummary = z.infer<typeof VerseSummarySchema>;

export const VerseWithWordsResponseSchema = z.object({
  id: z.number().int(),
  verse_num: z.number().int(),
  book_id: z.number().int(),
  chapter_num: z.number().int(),
  words: z.array(WordResponseSchema),
});

export type VerseWithWordsResponse = z.infer<typeof VerseWithWordsResponseSchema>;

export const VersesListResponseSchema = z.object({
  data: z.array(VerseWithWordsResponseSchema),
  total: z.number().int(),
});

export type VersesListResponse = z.infer<typeof VersesListResponseSchema>;

export const ChapterWithVersesResponseSchema = z.object({
  id: z.number().int(),
  book_id: z.number().int(),
  chapter_num: z.number().int(),
  verses: z.array(VerseSummarySchema),
});

export type ChapterWithVersesResponse = z.infer<typeof ChapterWithVersesResponseSchema>;

// ── Morphology ────────────────────────────────────────────────────────────────

export const MorphemeSchema = z.object({
  segment_index: z.number().int(),
  language: z.string(),
  part_of_speech: z.string(),
  pos_code: z.string(),
  gender: z.string().nullable().optional(),
  number: z.string().nullable().optional(),
  state: z.string().nullable().optional(),
  verb_stem: z.string().nullable().optional(),
  verb_aspect: z.string().nullable().optional(),
  person: z.string().nullable().optional(),
});

export type Morpheme = z.infer<typeof MorphemeSchema>;

export const WordWithMorphologyResponseSchema = z.object({
  id: z.number().int(),
  position: z.number().int(),
  surface_he: z.string(),
  display_he: z.string().nullable(),
  lemma_strong: z.string().nullable(),
  morph_code: z.string().nullable(),
  morphemes: z.array(MorphemeSchema),
});

export type WordWithMorphologyResponse = z.infer<typeof WordWithMorphologyResponseSchema>;