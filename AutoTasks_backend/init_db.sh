#!/bin/bash
# Database initialization script
set -e

# TODO: 'rule of least privelage': Don't give all privelages to django_user, only what's necessary
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER django_user WITH PASSWORD '$POSTGRES_PASSWORD';
    CREATE DATABASE autotasks_database;
    GRANT ALL PRIVILEGES ON DATABASE autotasks_database TO django_user;
EOSQL