/**
 * VerseReader — renders verses with clickable Hebrew words.
 * Clicking a word triggers morphology lookup.
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
    <div className="space-y-4" role="list" aria-label="Verses">
      {verses.map((verse) => (
        <div
          key={verse.id}
          role="listitem"
          className="flex gap-3 items-start"
        >
          {/* Verse number */}
          <span
            className="text-xs text-stone-400 font-mono mt-1 w-6 shrink-0 text-right select-none"
            aria-label={`Verse ${verse.verse_num}`}
          >
            {verse.verse_num}
          </span>

          {/* Hebrew words — RTL */}
          <p
            className="verse-line flex-1 text-2xl leading-loose"
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
                aria-label={`Word: ${word.surface_he}${word.lemma_strong ? ` (${word.lemma_strong})` : ""}`}
                aria-pressed={selectedWordId === word.id}
              >
                {word.surface_he}
              </button>
            ))}
          </p>
        </div>
      ))}
    </div>
  );
}
