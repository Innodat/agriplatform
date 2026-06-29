# Context: Error Payload Shape
version: 1.0.0
source: platform/prompts/tasks/error-payload.md@1.0.0
app_overrides: false

## Standard error response (all API endpoints)
```python
# FastAPI (Python)
from pydantic import BaseModel
from typing import Any, Optional

class ErrorResponse(BaseModel):
    error: str
    code: Optional[int] = None
    details: Optional[Any] = None
```

```typescript
// Frontend (TypeScript)
interface ErrorResponse {
  error: string;
  code?: number;
  details?: unknown;
}
```

## Usage
- Always return this shape on errors — never raw exception messages to the client.
- HTTP status codes: 400 (validation), 401 (auth), 403 (forbidden), 404 (not found), 500 (server).
- Log full error server-side; return sanitised message to client.
