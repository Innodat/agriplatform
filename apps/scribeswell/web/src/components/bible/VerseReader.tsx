/**
 * VerseReader — renders verses with clickable Hebrew words.
 * Clicking a word triggers morphology lookup.
 *
 * Layout per verse row (CSS grid, dir="ltr" on the row):
 *   col 1 (w-6, left)  : verse number
 *   col 2 (flex-1, right): Hebrew text block (dir="rtl" internally)
 *
 * Using an explicit LTR grid guarantees col 1 is always on the left
 * regardless of any inherited direction context.
 */
import type {
  VerseWithWordsResponse,
  WordResponse,
} from "@/schemas/bible.schema";

interface VerseReaderProps {
  verses: VerseWithWordsResponse[];
  selectedWordId: number | null;
  onWordClick: (word: WordResponse) => void;
}

export function VerseReader({
  verses,
  selectedWordId,
  onWordClick,
}: VerseReaderProps) {
  if (!verses.length) {
    return (
      <p className="text-stone-400 text-sm italic">No verses found.</p>
    );
  }

  return (
    <div className="space-y-0" role="list" aria-label="Verses">
      {verses.map((verse) => (
        <div
          key={verse.id}
          role="listitem"
          // dir="ltr" on the row so grid columns are always left=col1, right=col2.
          // The Hebrew <p> inside col2 overrides direction back to RTL.
          dir="rtl"
          className="grid items-baseline"
          style={{ gridTemplateColumns: "1.5rem 1fr" }}
        >
          {/* Col 1: verse number — always on the left */}
          <span
            className="text-xs text-stone-400 font-mono select-none text-right pr-1 pt-px"
            aria-label={`Verse ${verse.verse_num}`}
          >
            {verse.verse_num}
          </span>

          {/* Col 2: Hebrew text — RTL within its column */}
          <p
            className="verse-line text-xl"
            style={{ lineHeight: "1.9" }}
            dir="rtl"
            lang="he"
          >
            {verse.words.map((word) => (
              <button
                key={word.id}
                onClick={() => onWordClick(word)}
                className={`word-token inline-block mx-0.5 ${
                  selectedWordId === word.id ? "selected" : ""
                }`}
                aria-label={`Word: ${word.display_he}${word.lemma_strong ? ` (${word.lemma_strong})` : ""}`}
                aria-pressed={selectedWordId === word.id}
              >
                {word.display_he}
              </button>
            ))}
          </p>
        </div>
      ))}
    </div>
  );
}
