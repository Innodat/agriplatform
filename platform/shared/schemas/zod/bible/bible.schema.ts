// GENERATED — do not edit
// Source: Supabase bible schema — Phase 1
// Regenerate with: python tools/py/generate_models.py

import { z } from "zod";

// ── Enums ─────────────────────────────────────────────────────────────────────

export const TestamentSchema = z.enum(["torah", "nevi_im", "ketuvim"]);
export type Testament = z.infer<typeof TestamentSchema>;

export const LanguageSchema = z.enum(["hebrew", "aramaic"]);
export type Language = z.infer<typeof LanguageSchema>;

// ── Row schemas (match DB columns exactly) ────────────────────────────────────

export const BookRowSchema = z.object({
  id: z.number().int(),
  osis_id: z.string(),
  name_en: z.string(),
  name_he: z.string(),
  testament: TestamentSchema,
  book_order: z.number().int(),
});
export type BookRow = z.infer<typeof BookRowSchema>;

export const ChapterRowSchema = z.object({
  id: z.number().int(),
  book_id: z.number().int(),
  chapter_num: z.number().int(),
});
export type ChapterRow = z.infer<typeof ChapterRowSchema>;

export const VerseRowSchema = z.object({
  id: z.number().int(),
  chapter_id: z.number().int(),
  verse_num: z.number().int(),
  book_id: z.number().int(),
  chapter_num: z.number().int(),
});
export type VerseRow = z.infer<typeof VerseRowSchema>;

export const WordRowSchema = z.object({
  id: z.number().int(),
  verse_id: z.number().int(),
  position: z.number().int(),
  surface_he: z.string(),
  display_he: z.string().nullable(),
  lemma_strong: z.string().nullable(),
  morph_code: z.string().nullable(),
});
export type WordRow = z.infer<typeof WordRowSchema>;

export const MorphemeRowSchema = z.object({
  id: z.number().int(),
  word_id: z.number().int(),
  segment_index: z.number().int(),
  language: LanguageSchema,
  part_of_speech: z.string(),
  pos_code: z.string(),
  gender: z.string().nullable(),
  number: z.string().nullable(),
  state: z.string().nullable(),
  verb_stem: z.string().nullable(),
  verb_aspect: z.string().nullable(),
  person: z.string().nullable(),
});
export type MorphemeRow = z.infer<typeof MorphemeRowSchema>;

// ── API response schemas ──────────────────────────────────────────────────────

export const BookResponseSchema = BookRowSchema;
export type BookResponse = BookRow;

export const ChapterSummarySchema = z.object({
  id: z.number().int(),
  chapter_num: z.number().int(),
});
export type ChapterSummary = z.infer<typeof ChapterSummarySchema>;

export const BookWithChaptersResponseSchema = BookResponseSchema.extend({
  chapters: z.array(ChapterSummarySchema),
});
export type BookWithChaptersResponse = z.infer<typeof BookWithChaptersResponseSchema>;

export const VerseSummarySchema = z.object({
  id: z.number().int(),
  verse_num: z.number().int(),
});
export type VerseSummary = z.infer<typeof VerseSummarySchema>;

export const ChapterWithVersesResponseSchema = z.object({
  id: z.number().int(),
  book_id: z.number().int(),
  chapter_num: z.number().int(),
  verses: z.array(VerseSummarySchema),
});
export type ChapterWithVersesResponse = z.infer<typeof ChapterWithVersesResponseSchema>;

export const MorphemeResponseSchema = z.object({
  segment_index: z.number().int(),
  language: LanguageSchema,
  part_of_speech: z.string(),
  pos_code: z.string(),
  gender: z.string().nullable(),
  number: z.string().nullable(),
  state: z.string().nullable(),
  verb_stem: z.string().nullable(),
  verb_aspect: z.string().nullable(),
  person: z.string().nullable(),
});
export type MorphemeResponse = z.infer<typeof MorphemeResponseSchema>;

export const WordResponseSchema = z.object({
  id: z.number().int(),
  position: z.number().int(),
  surface_he: z.string(),
  display_he: z.string().nullable(),
  lemma_strong: z.string().nullable(),
  morph_code: z.string().nullable(),
});
export type WordResponse = z.infer<typeof WordResponseSchema>;

export const WordWithMorphologyResponseSchema = WordResponseSchema.extend({
  morphemes: z.array(MorphemeResponseSchema),
});
export type WordWithMorphologyResponse = z.infer<typeof WordWithMorphologyResponseSchema>;

export const VerseWithWordsResponseSchema = z.object({
  id: z.number().int(),
  verse_num: z.number().int(),
  book_id: z.number().int(),
  chapter_num: z.number().int(),
  words: z.array(WordResponseSchema),
});
export type VerseWithWordsResponse = z.infer<typeof VerseWithWordsResponseSchema>;

export const BooksListResponseSchema = z.object({
  data: z.array(BookResponseSchema),
  total: z.number().int(),
});
export type BooksListResponse = z.infer<typeof BooksListResponseSchema>;

export const VersesListResponseSchema = z.object({
  data: z.array(VerseWithWordsResponseSchema),
  total: z.number().int(),
});
export type VersesListResponse = z.infer<typeof VersesListResponseSchema>;
