/**
 * BookChapterSelector — compact dropdown selector for book + chapter navigation.
 *
 * Replaces the bulky left-sidebar BookList + ChapterNav pattern.
 *
 * Layout (when open):
 * ┌─────────────────────────────────────────────┐
 * │ [Torah]              │  א  ב  ג  ד  ה  …   │
 * │   Genesis / בראשית ◀ │                      │
 * │   Exodus  / שמות     │                      │
 * │ [Nevi'im]            │                      │
 * └─────────────────────────────────────────────┘
 *
 * Hover (or click on touch) a book → right panel shows its chapters.
 * Click a chapter → onSelect(osisId, chapterNum) → dropdown closes.
 * Escape or click-outside closes without navigating.
 */
import {
  useState,
  useRef,
  useEffect,
  useCallback,
  type KeyboardEvent,
} from "react";
import { ChevronDown } from "lucide-react";
import type {
  BookResponse,
  BookWithChaptersResponse,
} from "@/schemas/bible.schema";
import { useBook } from "@/hooks/useBible";
import { toHebrewOrdinal } from "@/lib/hebrew-ordinal";

// ── Constants ─────────────────────────────────────────────────────────────────

const DIVISION_ORDER = ["torah", "nevi_im", "ketuvim"] as const;
type Division = (typeof DIVISION_ORDER)[number];

const DIVISION_LABELS: Record<Division, string> = {
  torah: "Torah",
  nevi_im: "Nevi'im",
  ketuvim: "Ketuvim",
};

/**
 * Normalise a division string from the API to a known Division key.
 * The DB may return "nevi'im", "neviim", "Nevi'im" etc. — this is defensive.
 */
function normaliseDivision(raw: string): Division {
  const s = raw.toLowerCase().replace(/[^a-z]/g, "");
  if (s === "torah") return "torah";
  if (s.startsWith("nev")) return "nevi_im";
  if (s.startsWith("ket")) return "ketuvim";
  // fallback: return as-is cast — still shows under matching group or is skipped
  return "torah";
}

// ── Types ─────────────────────────────────────────────────────────────────────

interface BookChapterSelectorProps {
  /** All books from useBooks() */
  books: BookResponse[];
  /** Currently active book OSIS ID (e.g. "Gen") */
  selectedOsisId: string | null;
  /** Currently active chapter number */
  selectedChapter: number | null;
  /** Called when the user picks a book + chapter */
  onSelect: (osisId: string, chapterNum: number) => void;
}

// ── Sub-component: Chapter grid panel ─────────────────────────────────────────

interface ChapterPanelProps {
  bookData: BookWithChaptersResponse | null;
  loading: boolean;
  selectedOsisId: string | null;
  hoveredOsisId: string | null;
  selectedChapter: number | null;
  onChapterClick: (chapterNum: number) => void;
}

function ChapterPanel({
  bookData,
  loading,
  selectedOsisId,
  selectedChapter,
  onChapterClick,
}: ChapterPanelProps) {
  // Only show spinner when actively loading a real book (not the null/initial state).
  if (loading && !bookData) {
    return (
      <div className="flex items-center justify-center h-full py-8">
        <span className="text-xs text-stone-400 animate-pulse">Loading…</span>
      </div>
    );
  }

  if (!bookData) {
    return (
      <div className="flex items-center justify-center h-full py-8">
        <span className="text-xs text-stone-400">Hover a book</span>
      </div>
    );
  }

  const isActiveBook = bookData.osis_id === selectedOsisId;

  return (
    <div
      role="group"
      aria-label={`Chapters of ${bookData.name_en}`}
      className="flex flex-col h-full"
    >
      {/* Book name header inside the chapter panel */}
      <div className="px-3 py-2 border-b border-stone-100 flex items-center justify-between gap-2 shrink-0">
        <span className="text-xs font-semibold text-stone-500 uppercase tracking-wider">
          {bookData.name_en}
        </span>
        <span className="text-sm font-medium text-stone-600" dir="rtl" lang="he">
          {bookData.name_he}
        </span>
      </div>

      {/* Chapter grid — dir="rtl" so auto-fill flows right-to-left (א top-right) */}
      <div className="p-2 overflow-y-auto flex-1" style={{ maxHeight: "18rem" }}>
        <div
          className="grid gap-1"
          dir="rtl"
          style={{ gridTemplateColumns: "repeat(auto-fill, minmax(2.5rem, 1fr))" }}
        >
          {bookData.chapters.map((ch) => {
            const isActive = isActiveBook && selectedChapter === ch.chapter_num;
            return (
              <button
                key={ch.id}
                type="button"
                onClick={() => onChapterClick(ch.chapter_num)}
                className={[
                  "h-10 w-full rounded-md text-sm font-medium transition-colors",
                  "focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400",
                  isActive
                    ? "bg-amber-500 text-white"
                    : "bg-stone-100 text-stone-700 hover:bg-amber-100 hover:text-amber-900",
                ].join(" ")}
                aria-label={`Chapter ${ch.chapter_num} of ${bookData.name_en}`}
                aria-current={isActive ? "page" : undefined}
                dir="rtl"
                lang="he"
              >
                {toHebrewOrdinal(ch.chapter_num)}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export function BookChapterSelector({
  books,
  selectedOsisId,
  selectedChapter,
  onSelect,
}: BookChapterSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [hoveredOsisId, setHoveredOsisId] = useState<string | null>(
    selectedOsisId
  );

  // Fetch chapters for the hovered book only while dropdown is open.
  const hoveredBook = useBook(isOpen ? hoveredOsisId : null);

  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  // Sync hovered book to selected book when dropdown opens.
  useEffect(() => {
    if (isOpen) setHoveredOsisId(selectedOsisId);
  }, [isOpen, selectedOsisId]);

  // Close on outside click.
  useEffect(() => {
    if (!isOpen) return;
    function handleOutside(e: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, [isOpen]);

  // Close on Escape.
  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLDivElement>) => {
      if (e.key === "Escape" && isOpen) {
        setIsOpen(false);
        triggerRef.current?.focus();
      }
    },
    [isOpen]
  );

  function handleChapterClick(chapterNum: number) {
    if (!hoveredOsisId) return;
    onSelect(hoveredOsisId, chapterNum);
    setIsOpen(false);
    triggerRef.current?.focus();
  }

  const grouped = books.reduce<Partial<Record<Division, BookResponse[]>>>(
    (acc, book) => {
      const d = normaliseDivision(book.division);
      if (!acc[d]) acc[d] = [];
      acc[d]!.push(book);
      return acc;
    },
    {}
  );

  const activeBook = books.find((b) => b.osis_id === selectedOsisId);
  const chapterLabel =
    selectedChapter !== null ? toHebrewOrdinal(selectedChapter) : null;

  return (
    <div ref={containerRef} className="relative" onKeyDown={handleKeyDown}>
      {/* ── Trigger ──────────────────────────────────────────────────── */}
      <button
        ref={triggerRef}
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-haspopup="dialog"
        aria-expanded={isOpen}
        aria-label={
          activeBook
            ? `Navigate: ${activeBook.name_en}, chapter ${selectedChapter ?? 1}. Open selector.`
            : "Open book and chapter selector"
        }
        className={[
          "inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border",
          "text-sm font-medium transition-colors",
          "focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400",
          isOpen
            ? "bg-amber-50 text-amber-900 border-amber-200"
            : "text-stone-700 border-transparent hover:bg-stone-100 hover:border-stone-200",
        ].join(" ")}
      >
        <span>{activeBook?.name_en ?? "Select book"}</span>
        {chapterLabel && (
          <span className="text-stone-400 select-none" aria-hidden="true">
            ›
          </span>
        )}
        {chapterLabel && (
          <span
            className="font-medium text-amber-700"
            dir="rtl"
            lang="he"
            aria-hidden="true"
          >
            {chapterLabel}
          </span>
        )}
        <ChevronDown
          className={[
            "w-4 h-4 text-stone-400 transition-transform duration-150",
            isOpen ? "rotate-180" : "",
          ].join(" ")}
          aria-hidden="true"
        />
      </button>


      {/* ── Dropdown panel ──────────────────────────────────────────── */}
      {isOpen && (
        <div
          role="dialog"
          aria-label="Book and chapter selector"
          className={[
            "absolute right-0 top-full mt-2 z-50",
            "bg-white border border-stone-200 rounded-xl shadow-xl",
            "flex overflow-hidden",
            "w-[28rem]",
          ].join(" ")}
          onMouseDown={(e) => e.stopPropagation()}
        >
          {/* Left: Book list */}
          <nav
            aria-label="Books of the Tanakh"
            className="w-48 shrink-0 border-r border-stone-100 overflow-y-auto"
            style={{ maxHeight: "22rem" }}
          >
            {DIVISION_ORDER.map((division) => {
              const group = grouped[division];
              if (!group?.length) return null;
              return (
                <div key={division} className="py-1">
                  <div className="px-3 py-1.5">
                    <span className="text-[0.65rem] font-semibold uppercase tracking-widest text-stone-400">
                      {DIVISION_LABELS[division]}
                    </span>
                  </div>
                  <ul>
                    {group.map((book) => {
                      const isActive = book.osis_id === selectedOsisId;
                      const isHovered = book.osis_id === hoveredOsisId;
                      return (
                        <li key={book.osis_id}>
                          <button
                            type="button"
                            onMouseEnter={() => setHoveredOsisId(book.osis_id)}
                            onClick={() => setHoveredOsisId(book.osis_id)}
                            aria-current={isActive ? "page" : undefined}
                            aria-label={`${book.name_en} — ${book.name_he}`}
                            className={[
                              "w-full text-left px-3 py-1.5 text-sm transition-colors",
                              "focus:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-amber-400",
                              isActive
                                ? "bg-amber-100 text-amber-900 font-medium"
                                : isHovered
                                ? "bg-stone-100 text-stone-900"
                                : "text-stone-700 hover:bg-stone-50",
                            ].join(" ")}
                          >
                            <span className="flex items-center justify-between gap-1 min-w-0">
                              <span className="truncate">{book.name_en}</span>
                              <span
                                className="text-xs text-stone-400 shrink-0"
                                dir="rtl"
                                lang="he"
                              >
                                {book.name_he}
                              </span>
                            </span>
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              );
            })}
          </nav>

          {/* Right: Chapter grid */}
          <div className="flex-1 min-w-0">
            <ChapterPanel
              bookData={hoveredBook.data}
              loading={hoveredBook.loading}
              selectedOsisId={selectedOsisId}
              hoveredOsisId={hoveredOsisId}
              selectedChapter={selectedChapter}
              onChapterClick={handleChapterClick}
            />
          </div>
        </div>
      )}
    </div>
  );
}

