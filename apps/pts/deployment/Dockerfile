# Frozen Python3.15 runtime; no installer/network work during the image build.
FROM python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e AS verified
COPY apps/pts /binding
RUN ["/binding/runtime-bundle/python/bin/python3.15", "-B", "/binding/deployment/verify_runtime.py", "--root", "/binding", "--bundle", "/binding/runtime-bundle"]
FROM python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e
COPY --from=verified --chown=65532:65532 /binding/runtime-bundle/python /opt/python
COPY --from=verified --chown=65532:65532 /binding/runtime-bundle/site-packages /opt/site-packages
COPY --from=verified --chown=65532:65532 /binding/runtime-bundle/owner-code /srv
ENV PATH=/opt/python/bin:$PATH PYTHONPATH=/opt/site-packages PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv
USER 65532:65532
EXPOSE 8000
HEALTHCHECK --interval=5s --timeout=2s --start-period=10s --retries=4 CMD ["/opt/python/bin/python3.15", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=1)"]
CMD ["/opt/python/bin/python3.15", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--log-level", "critical", "--timeout-graceful-shutdown", "20"]
