-- Database: usstatesdb
DROP DATABASE usstatesdb;

CREATE DATABASE usstatesdb
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

\connect usstatesdb;

CREATE SCHEMA tiger AUTHORIZATION postgres;

CREATE SCHEMA topology AUTHORIZATION postgres;

COMMENT ON SCHEMA topology IS 'PostGIS Topology schema';

ALTER DATABASE usstatesdb SET search_path TO "$user", public, tiger;

GRANT CONNECT ON DATABASE usstatesdb TO postgres;
GRANT USAGE ON SCHEMA public TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON DATABASE usstatesdb TO postgres;

CREATE EXTENSION address_standardizer SCHEMA public;
CREATE EXTENSION fuzzystrmatch SCHEMA public;
CREATE EXTENSION postgis SCHEMA public;
CREATE EXTENSION postgis_sfcgal SCHEMA public;
CREATE EXTENSION postgis_tiger_geocoder SCHEMA tiger;
CREATE EXTENSION postgis_topology SCHEMA topology;
