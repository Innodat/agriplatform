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
  lexical_id: z.string().nullable().optional(),
  match_key: z.string().nullable().optional(),
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
  lexical_id: z.string().nullable().optional(),
  match_key: z.string().nullable().optional(),
  morphemes: z.array(MorphemeSchema),
});

export type WordWithMorphologyResponse = z.infer<typeof WordWithMorphologyResponseSchema>;
export type LexiconNode = {language?:string|null; direction?:string|null; kind:string; text:string; children?:LexiconNode[]; book?:string|null; chapter?:number|null; verse?:number|null};
const LexiconNodeSchema:z.ZodType<LexiconNode> = z.lazy(()=>z.object({language:z.string().nullable().optional(),direction:z.string().nullable().optional(),kind:z.string(),text:z.string(),children:z.array(LexiconNodeSchema).optional(),book:z.string().nullable().optional(),chapter:z.number().nullable().optional(),verse:z.number().nullable().optional()}));
export const LexiconSchema = z.object({status:z.enum(['available','missing','unavailable']),lexical_id:z.string(),lemma:z.string().default(''),transliteration:z.string().default(''),definition:z.string().default(''),root:z.object({id:z.string(),text:z.string()}).nullable().optional(),pronunciation:z.string().default(''),strong_definition:z.string().default(''),strong_usage:z.string().default(''),strong_source:z.string().default(''),bdb:z.array(LexiconNodeSchema).default([]),bdb_status:z.string().default('missing')});
export const OccurrencesSchema = z.object({data:z.array(z.object({id:z.number(),position:z.number(),surface_he:z.string(),display_he:z.string().nullable(),book:z.string(),book_name:z.string(),chapter:z.number(),verse:z.number()})),total:z.number(),verse_total:z.number(),offset:z.number(),limit:z.number()});
