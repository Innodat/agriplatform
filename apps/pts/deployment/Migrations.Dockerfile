FROM python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e AS verified
COPY apps/pts /binding
RUN ["/binding/runtime-bundle/python/bin/python3.15", "-B", "/binding/deployment/verify_runtime.py", "--root", "/binding", "--bundle", "/binding/runtime-bundle"]
FROM python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH=/opt/python/bin:$PATH PYTHONPATH=/opt/site-packages
WORKDIR /app
COPY --from=verified --chown=10001:10001 /binding/runtime-bundle/python /opt/python
COPY --from=verified --chown=10001:10001 /binding/runtime-bundle/site-packages /opt/site-packages
COPY apps/pts/backend/ apps/pts/backend/
COPY apps/pts/tools/bind_corpus.py apps/pts/tools/bind_corpus.py
COPY tools/py/deploy_pts.py tools/py/deploy_pts.py
COPY apps/pts/alembic.ini apps/pts/alembic.ini
COPY apps/pts/migrations/ apps/pts/migrations/
COPY services/access/alembic.ini services/access/alembic.ini
COPY services/access/migrations/ services/access/migrations/
COPY services/content-service/alembic.ini services/content-service/alembic.ini
COPY services/content-service/migrations/ services/content-service/migrations/
COPY services/content-service/database-tools/ services/content-service/database-tools/
COPY apps/pts/deployment/migrate.py apps/pts/deployment/migrate.py
COPY platform/deployment/target_contract.py platform/deployment/target_contract.py
USER 10001:10001
ENTRYPOINT ["/opt/python/bin/python3.15", "apps/pts/deployment/migrate.py"]
