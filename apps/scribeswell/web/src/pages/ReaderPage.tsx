/** Public Hebrew reader with optional independent passage comparison. */
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Columns2, X } from "lucide-react";
import { PassagePane } from "@/components/bible/PassagePane";
import { MorphologyPanel } from "@/components/bible/MorphologyPanel";
import { useBooks, useWordMorphology } from "@/hooks/useBible";
import type { WordResponse } from "@/schemas/bible.schema";

type Pane = 1 | 2;
type Selection = { pane: Pane; book: string; chapter: number; verse: number; word: WordResponse };
function chapterNumber(value: string | null) {
  const number = Number(value);
  return Number.isSafeInteger(number) && number > 0 && number <= 150 ? number : 1;
}
const control = "inline-flex items-center justify-center gap-2 rounded-lg border border-stone-200 px-3 py-1.5 text-sm text-stone-700 hover:bg-stone-100 focus-visible:outline-2 focus-visible:outline-amber-600";

export function ReaderPage() {
  const [params, setParams] = useSearchParams();
  const book = params.get('book') || 'Gen';
  const chapter = chapterNumber(params.get('chapter'));
  const compareBook = params.get('compareBook') || '';
  const compareChapter = chapterNumber(params.get('compareChapter'));
  const comparing = Boolean(compareBook);
  const [mobilePane, setMobilePane] = useState<Pane>(1);
  const [selection, setSelection] = useState<Selection | null>(null);
  // Validate against URL on every render, including history navigation. Never
  // briefly attribute the old word to the newly selected passage.
  const selected = selection && (selection.pane === 1
    ? selection.book === book && selection.chapter === chapter
    : comparing && selection.book === compareBook && selection.chapter === compareChapter) ? selection : null;
  useEffect(() => { if (!selected) setSelection(null); }, [selected]);
  useEffect(() => { if (!comparing) setMobilePane(1); }, [comparing]);
  const books = useBooks();
  const morphology = useWordMorphology(selected?.word.id ?? null);
  const bookName = (osis: string) => books.data?.data.find(b => b.osis_id === osis)?.name_en ?? osis;
  const context = selected ? `${comparing ? `Passage ${selected.pane} · ` : ''}${bookName(selected.book)} ${selected.chapter}:${selected.verse}` : '';

  function navigate(pane: Pane, nextBook: string, nextChapter: number) {
    if (selection?.pane === pane) setSelection(null);
    setParams(previous => {
      const next = new URLSearchParams(previous);
      next.set(pane === 1 ? 'book' : 'compareBook', nextBook);
      next.set(pane === 1 ? 'chapter' : 'compareChapter', String(nextChapter));
      return next;
    });
  }
  function toggleComparison() {
    if (comparing) {
      if (selection?.pane === 2) setSelection(null);
      setMobilePane(1);
      setParams(previous => { const next = new URLSearchParams(previous); next.delete('compareBook'); next.delete('compareChapter'); return next; });
    } else {
      setSelection(null);
      navigate(2, book, chapter);
      setMobilePane(2);
    }
  }
  function chooseWord(pane: Pane, word: WordResponse, verse: number) {
    setMobilePane(pane);
    setSelection(previous => previous?.pane === pane && previous.word.id === word.id ? null : {
      pane, word, verse, book: pane === 1 ? book : compareBook, chapter: pane === 1 ? chapter : compareChapter,
    });
  }
  function showPane(pane: Pane) {
    setMobilePane(pane);
    // Keep analysis attached to the visible passage on narrow screens.
    if (selection?.pane !== pane) setSelection(null);
  }

  return (
    <div className={`flex flex-col gap-3 h-full min-h-0 mx-auto ${comparing ? 'max-w-[100rem]' : 'max-w-5xl'}`}>
      <div className="flex flex-wrap shrink-0 items-center gap-2">
        <button type="button" className={control} onClick={toggleComparison} aria-pressed={comparing}>
          {comparing ? <X size={16} aria-hidden="true" /> : <Columns2 size={16} aria-hidden="true" />}
          {comparing ? 'Close comparison' : 'Compare passages'}
        </button>
        {books.loading && <span className="text-sm text-stone-400">Loading books…</span>}
        {books.error && <p role="alert" className="text-sm text-red-700">Could not load books. <button className="underline" onClick={books.refetch}>Retry books</button></p>}
      </div>
      {comparing && <div role="group" aria-label="Visible passage" className="flex gap-2 shrink-0 lg:hidden">
        {([1, 2] as const).map(pane => <button key={pane} className={`${control} flex-1 min-w-0 ${mobilePane === pane ? 'bg-amber-100 border-amber-300' : ''}`} aria-controls={`passage-${pane}`} aria-label={`Show passage ${pane}: ${bookName(pane === 1 ? book : compareBook)} ${pane === 1 ? chapter : compareChapter}`} aria-pressed={mobilePane === pane} onClick={() => showPane(pane)}>
          <span className="truncate">{pane}: {bookName(pane === 1 ? book : compareBook)} {pane === 1 ? chapter : compareChapter}</span>
        </button>)}
      </div>}
      <div className={`flex flex-col gap-4 flex-1 min-h-0 ${comparing ? 'xl:flex-row' : 'md:flex-row md:justify-center'}`}>
        <div className={`flex gap-4 flex-1 min-w-0 min-h-0 ${comparing ? '' : 'md:max-w-[44rem]'}`}>
          <PassagePane number={1} book={book} chapter={chapter} books={books.data?.data ?? []} comparing={comparing} visible={!comparing || mobilePane === 1} selectedWordId={selected?.pane === 1 ? selected.word.id : null} onNavigate={(b,c) => navigate(1,b,c)} onWord={(w,v) => chooseWord(1,w,v)} />
          {comparing && <PassagePane number={2} book={compareBook} chapter={compareChapter} books={books.data?.data ?? []} comparing visible={mobilePane === 2} selectedWordId={selected?.pane === 2 ? selected.word.id : null} onNavigate={(b,c) => navigate(2,b,c)} onWord={(w,v) => chooseWord(2,w,v)} />}
        </div>
        {selected && <aside aria-label="Word analysis panel" className={`min-h-0 max-h-[45%] overflow-y-auto overscroll-contain shrink-0 ${comparing ? 'xl:max-h-full xl:h-full xl:w-72' : 'md:max-h-full md:h-full md:w-72'}`}>
          {morphology.loading && <p role="status" className="p-4 bg-white">Loading word analysis… <button className="underline" onClick={() => setSelection(null)}>Close</button></p>}
          {morphology.error && <p role="alert" className="bg-white p-4 text-sm text-red-700">Could not load word analysis. <button className="underline" onClick={morphology.refetch}>Retry word analysis</button><button className="ml-2 underline" onClick={() => setSelection(null)}>Close</button></p>}
          {morphology.data && morphology.data.id === selected.word.id && <MorphologyPanel word={morphology.data} context={context} onClose={() => setSelection(null)} />}
        </aside>}
      </div>
    </div>
  );
}
