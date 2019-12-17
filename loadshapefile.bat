@echo off

IF %1.==. GOTO No1
IF %2.==. GOTO No2
IF %3.==. GOTO No3
IF %4.==. GOTO No4

REM export a password for use with the system (no quotes)
SET PGHOST=%1
SET PGDATABASE=usstatesdb
SET PGUSER=%2
SET PGPASSWORD=%3
SET SHPFILEPATH=%4
shp2pgsql.exe -I -s 26918 %SHPFILEPATH%/tl_2019_us_state.shp public.tl_2019_us_state | psql -h %PGHOST% -U %PGUSER% -d %PGDATABASE%
GOTO End1

:No1
  ECHO Usage: loadshapefile.bat hostname username password shapefilepath - hostname parameter incorrect
GOTO End1
:No2
  ECHO Usage: loadshapefile.bat hostname username password shapefilepath - username parameter incorrect
GOTO End1
:No3
  ECHO Usage: loadshapefile.bat hostname username password shapefilepath - password parameter incorrect
GOTO End1
:No4
  ECHO Usage: loadshapefile.bat hostname username password shapefilepath - password parameter incorrect
GOTO End1

:End1

