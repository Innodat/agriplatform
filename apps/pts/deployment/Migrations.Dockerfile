FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY apps/pts/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && useradd --uid 10001 api
COPY tools/py/deploy_pts.py tools/py/deploy_pts.py
COPY apps/pts/alembic.ini apps/pts/alembic.ini
COPY apps/pts/migrations/ apps/pts/migrations/
COPY services/access/alembic.ini services/access/alembic.ini
COPY services/access/migrations/ services/access/migrations/
COPY services/content-service/alembic.ini services/content-service/alembic.ini
COPY services/content-service/migrations/ services/content-service/migrations/
COPY apps/pts/deployment/migrate.py apps/pts/deployment/migrate.py
COPY platform/deployment/target_contract.py platform/deployment/target_contract.py
USER 10001:10001
ENTRYPOINT ["python", "apps/pts/deployment/migrate.py"]
