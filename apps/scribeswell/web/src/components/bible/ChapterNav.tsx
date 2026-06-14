/**
 * ChapterNav — chapter number grid for a selected book.
 */
import type { ChapterSummary } from "@/schemas/bible.schema";

interface ChapterNavProps {
  chapters: ChapterSummary[];
  selectedChapter: number | null;
  onSelect: (chapterNum: number) => void;
}

export function ChapterNav({
  chapters,
  selectedChapter,
  onSelect,
}: ChapterNavProps) {
  return (
    <div>
      <h3 className="text-xs font-semibold uppercase tracking-wider text-stone-400 mb-2 px-1">
        Chapters
      </h3>
      <div
        className="grid gap-1"
        style={{ gridTemplateColumns: "repeat(auto-fill, minmax(2.5rem, 1fr))" }}
        role="list"
        aria-label="Chapter list"
      >
        {chapters.map((ch) => (
          <button
            key={ch.id}
            onClick={() => onSelect(ch.chapter_num)}
            role="listitem"
            className={`h-10 w-full rounded-md text-sm font-medium transition-colors ${
              selectedChapter === ch.chapter_num
                ? "bg-amber-500 text-white"
                : "bg-stone-100 text-stone-700 hover:bg-amber-100 hover:text-amber-900"
            }`}
            aria-label={`Chapter ${ch.chapter_num}`}
            aria-current={selectedChapter === ch.chapter_num ? "page" : undefined}
          >
            {ch.chapter_num}
          </button>
        ))}
      </div>
    </div>
  );
}
