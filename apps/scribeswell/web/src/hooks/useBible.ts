/**
 * Data-fetching hooks for the Bible reader.
 * All calls go through the api-client → FastAPI → Supabase.
 */
import { useState, useEffect, useCallback } from "react";
import {
  getBooks,
  getBook,
  getVerses,
  getWordMorphology,
} from "@/lib/api-client";
import type {
  BooksListResponse,
  BookWithChaptersResponse,
  VersesListResponse,
  WordWithMorphologyResponse,
} from "@/schemas/bible.schema";

// ── Generic async hook ────────────────────────────────────────────────────────

interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useAsync<T>(
  fn: () => Promise<T>,
  deps: unknown[]
): AsyncState<T> & { refetch: () => void } {
  const [state, setState] = useState<AsyncState<T> & {request?: () => Promise<T>}>({
    data: null,
    loading: true,
    error: null,
  });

  const [revision,setRevision] = useState(0);
  // The caller supplies the identity of the requested book/chapter/word.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const fetchData = useCallback(fn,deps);
  useEffect(() => {
    let active = true;
    setState({request:fetchData,data:null,loading:true,error:null});
    fetchData().then(data=>{
      if(active)setState({request:fetchData,data,loading:false,error:null});
    }).catch((err:unknown)=>{
      if(active)setState({request:fetchData,data:null,loading:false,error:err instanceof Error?err.message:'Unable to load the reader.'});
    });
    return ()=>{active=false;};
  },[fetchData,revision]);
  return {...(state.request===fetchData?state:{data:null,loading:true,error:null}),refetch:()=>setRevision(value=>value+1)};
}

// ── Public hooks ──────────────────────────────────────────────────────────────

export function useBooks() {
  return useAsync<BooksListResponse>(() => getBooks(), []);
}

export function useBook(osisId: string | null) {
  return useAsync<BookWithChaptersResponse | null>(
    () => (osisId ? getBook(osisId) : Promise.resolve(null)),
    [osisId]
  );
}

export function useVerses(osisId: string | null, chapterNum: number | null) {
  return useAsync<VersesListResponse | null>(
    () =>
      osisId && chapterNum
        ? getVerses(osisId, chapterNum)
        : Promise.resolve(null),
    [osisId, chapterNum]
  );
}

export function useWordMorphology(wordId: number | null) {
  return useAsync<WordWithMorphologyResponse | null>(
    () => (wordId ? getWordMorphology(wordId) : Promise.resolve(null)),
    [wordId]
  );
}
