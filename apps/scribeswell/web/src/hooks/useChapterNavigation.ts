import { useBook } from "./useBible";
import type { BookResponse, BookWithChaptersResponse } from "@/schemas/bible.schema";

type Target = { book: string; chapter: number };
function chapters(data: BookWithChaptersResponse | null) {
  return data ? [...data.chapters].sort((a, b) => a.chapter_num - b.chapter_num) : [];
}

/** Follow the existing catalogue order and actual chapter lists, never counts. */
export function useChapterNavigation(books: BookResponse[], book: string, chapter: number) {
  const current = useBook(book);
  // useBook can retain the prior response until its effect starts. Do not use
  // it for a different reference, even during that first render.
  const currentChapters = chapters(!current.loading && current.data?.osis_id === book ? current.data : null);
  const chapterIndex = currentChapters.findIndex(item => item.chapter_num === chapter);
  const bookIndex = books.findIndex(item => item.osis_id === book);
  const priorBook = chapterIndex === 0 && bookIndex > 0 ? books[bookIndex - 1] : null;
  const followingBook = chapterIndex >= 0 && chapterIndex === currentChapters.length - 1 && bookIndex >= 0 ? books[bookIndex + 1] : null;
  const prior = useBook(priorBook?.osis_id ?? null);
  const following = useBook(followingBook?.osis_id ?? null);
  const priorChapters = chapters(!prior.loading && prior.data?.osis_id === priorBook?.osis_id ? prior.data : null);
  const followingChapters = chapters(!following.loading && following.data?.osis_id === followingBook?.osis_id ? following.data : null);

  let previous: Target | null = null;
  let next: Target | null = null;
  if (chapterIndex > 0) previous = { book, chapter: currentChapters[chapterIndex - 1].chapter_num };
  else if (priorBook && priorChapters.length) previous = { book: priorBook.osis_id, chapter: priorChapters[priorChapters.length - 1].chapter_num };
  if (chapterIndex >= 0 && chapterIndex < currentChapters.length - 1) next = { book, chapter: currentChapters[chapterIndex + 1].chapter_num };
  else if (followingBook && followingChapters.length) next = { book: followingBook.osis_id, chapter: followingChapters[0].chapter_num };

  const failures = [current, ...(priorBook ? [prior] : []), ...(followingBook ? [following] : [])].filter(result => result.error);
  return { previous, next, error: failures.length > 0, retry: () => failures.forEach(result => result.refetch()) };
}
