FROM python:3.12-slim
WORKDIR /workspace
COPY apps/scribeswell/deployment/migration-requirements.txt /tmp/migration-requirements.txt
RUN pip install --no-cache-dir -r /tmp/migration-requirements.txt && useradd --uid 10001 --create-home migration
COPY apps/scribeswell/alembic.ini apps/scribeswell/alembic.ini
COPY apps/scribeswell/migrations apps/scribeswell/migrations
COPY apps/scribeswell/studies-alembic.ini apps/scribeswell/studies-alembic.ini
COPY apps/scribeswell/studies-migrations apps/scribeswell/studies-migrations
COPY apps/scribeswell/studies-database-tools apps/scribeswell/studies-database-tools
COPY apps/scribeswell/deployment/studies_release_contract.py apps/scribeswell/deployment/studies_release_contract.py
COPY apps/scribeswell/deployment/studies_migrate.py apps/scribeswell/deployment/studies_migrate.py
COPY apps/scribeswell/backend/database.py apps/scribeswell/backend/database.py
COPY apps/scribeswell/deployment/migrate.py apps/scribeswell/deployment/migrate.py
COPY apps/scribeswell/supabase/migrations/20260614000000_scribeswell_create_schema.sql apps/scribeswell/supabase/migrations/20260614000000_scribeswell_create_schema.sql
COPY apps/scribeswell/deployment/bootstrap/001_direct_database_roles.sql apps/scribeswell/deployment/bootstrap/001_direct_database_roles.sql
COPY platform/deployment/target_contract.py platform/deployment/target_contract.py
# Generated scaffold helper inputs can be0600 in the checkout. The restricted
# migration user must read/import the copied package; never edit generated files.
RUN chmod -R a+rX /workspace/apps/scribeswell/studies-database-tools
USER 10001:10001
ENTRYPOINT ["python", "apps/scribeswell/deployment/migrate.py"]
