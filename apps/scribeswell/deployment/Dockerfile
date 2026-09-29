FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY apps/scribeswell/backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && useradd --uid 10001 --create-home api
COPY apps/scribeswell/backend/ apps/scribeswell/backend/
COPY apps/scribeswell/data/hebrew-lexicon/ apps/scribeswell/data/hebrew-lexicon/
COPY apps/scribeswell/scripts/hebrew.json apps/scribeswell/scripts/hebrew.json
COPY apps/scribeswell/scripts/seed.py apps/scribeswell/scripts/seed.py
COPY apps/scribeswell/tools/py/import_bible.py apps/scribeswell/tools/py/import_bible.py
COPY apps/scribeswell/tools/py/oshb_morph.py apps/scribeswell/tools/py/oshb_morph.py
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=4 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"
CMD ["uvicorn", "main:app", "--app-dir", "apps/scribeswell/backend", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--log-level", "critical", "--timeout-graceful-shutdown", "20"]
