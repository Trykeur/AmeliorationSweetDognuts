SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'movie';

SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';

SELECT schema_name FROM information_schema.schemata;