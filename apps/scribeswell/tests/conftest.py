"""Isolate tests from workstation credentials and obsolete dotenv authority."""
import os
os.environ['SUPABASE_SECRET_KEY'] = ''
os.environ['SUPABASE_SERVICE_ROLE_KEY'] = ''
os.environ['SCRIBESWELL_DATABASE_URL'] = 'postgresql://scribeswell_runtime:fixture@127.0.0.1:1/postgres'
os.environ['APP_ENV'] = 'development'
