"""Create-once owner seed: health-only candidate shell, without protected routes."""
from fastapi import FastAPI
from safe_errors import install_safe_errors

app = FastAPI(title="{{OWNER}}", docs_url=None, redoc_url=None, openapi_url=None)
install_safe_errors(app)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
