"""Create-once owner seed: health-only candidate shell, without protected routes."""
from typing import Literal
from fastapi import FastAPI
from pydantic import BaseModel
from safe_errors import ErrorEnvelope, install_safe_errors


class HealthResponse(BaseModel):
    status: Literal["ok"]


app = FastAPI(title="{{OWNER}}", docs_url=None, redoc_url=None, openapi_url=None,
              servers=[{"url": "/api"}])
install_safe_errors(app)


@app.get("/health", operation_id="health", response_model=HealthResponse,
         response_model_exclude_none=True,
         responses={status: {"model": ErrorEnvelope} for status in (422, 500, 503)})
def health() -> HealthResponse:
    return HealthResponse(status="ok")
