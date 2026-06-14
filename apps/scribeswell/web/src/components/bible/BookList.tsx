/**
 * BookList — displays all 39 Tanakh books grouped by testament.
 */
import type { BookResponse } from "@/schemas/bible.schema";

const TESTAMENT_LABELS: Record<string, string> = {
  torah: "Torah",
  nevi_im: "Nevi'im",
  ketuvim: "Ketuvim",
};

interface BookListProps {
  books: BookResponse[];
  selectedOsisId: string | null;
  onSelect: (osisId: string) => void;
}

export function BookList({ books, selectedOsisId, onSelect }: BookListProps) {
  const grouped = books.reduce<Record<string, BookResponse[]>>((acc, book) => {
    if (!acc[book.testament]) acc[book.testament] = [];
    acc[book.testament].push(book);
    return acc;
  }, {});

  const testamentOrder = ["torah", "nevi_im", "ketuvim"];

  return (
    <nav aria-label="Books of the Tanakh">
      {testamentOrder.map((testament) => {
        const group = grouped[testament];
        if (!group?.length) return null;
        return (
          <div key={testament} className="mb-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-stone-400 mb-2 px-1">
              {TESTAMENT_LABELS[testament]}
            </h3>
            <ul className="space-y-0.5">
              {group.map((book) => (
                <li key={book.osis_id}>
                  <button
                    onClick={() => onSelect(book.osis_id)}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                      selectedOsisId === book.osis_id
                        ? "bg-amber-100 text-amber-900 font-medium"
                        : "text-stone-700 hover:bg-stone-100"
                    }`}
                    aria-current={
                      selectedOsisId === book.osis_id ? "page" : undefined
                    }
                  >
                    <span className="flex items-center justify-between">
                      <span>{book.name_en}</span>
                      <span
                        className="text-base font-hebrew text-stone-400"
                        dir="rtl"
                        lang="he"
                      >
                        {book.name_he}
                      </span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        );
      })}
    </nav>
  );
}
