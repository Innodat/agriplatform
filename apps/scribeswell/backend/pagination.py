"""Read complete, stable PostgREST result sets; detect count drift or truncation."""


def fetch_all(query, page_size: int = 500) -> list[dict]:
    rows = []
    expected = None
    while True:
        response = query.range(len(rows), len(rows) + page_size - 1).execute()
        count = response.count
        if count is None:
            raise RuntimeError('Pagination requires select(..., count="exact")')
        if expected is not None and expected != count:
            raise RuntimeError('Dataset changed during pagination; retry against a stable dataset')
        expected = count
        page = response.data
        if not page:
            if len(rows) != expected:
                raise RuntimeError(f'Incomplete query: expected {expected} rows, received {len(rows)}')
            return rows
        rows.extend(page)
        if len(rows) == expected:
            return rows
        if len(rows) > expected:
            raise RuntimeError('Query returned more rows than its exact count')
