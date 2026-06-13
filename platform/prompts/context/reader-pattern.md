# Context: Reader Pattern (Hebrew Bible app)
version: 1.0.0

## Domain model
```
Book → Chapter → Verse → Word → Morphology
```

## UI structure
```
<ReaderLayout>                      ← ui-business component (future)
  <BookNav />                       ← sidebar: book + chapter selector
  <VerseList chapter={...} />       ← main content: verses
    <VerseRow>
      <WordToken word={...} />      ← clickable word
    </VerseRow>
  <MorphologyPanel word={...} />    ← bottom/side panel: morphology detail
</ReaderLayout>
```

## File layout
```
apps/bible-web/src/
  pages/reader/
    index.tsx                       ← reader page entry
    components/
      book-nav.tsx
      verse-list.tsx
      word-token.tsx
      morphology-panel.tsx
  hooks/
    use-books.ts
    use-chapter.ts
    use-word-morphology.ts
```

## Data flow
```
Page → Hook → api-client (generated) → FastAPI → Supabase (bible schema)
```

## Key rules
- Read-only app: no mutations from UI (data loaded via import pipeline).
- Word selection is local state (no server round-trip for selection).
- Morphology panel loads on word click (lazy fetch).
- Navigation state in URL params: `?book=GEN&chapter=1`.
