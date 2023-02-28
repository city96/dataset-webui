@echo off

REM Available command line arguments:
REM --autolaunch   [Open webui in default browser]
REM --port 8080    [Port to host webui on]
REM --listen       [Allow access from LAN (NOT RECOMMENDED)]
set COMMANDLINE_ARGS=

if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
call python webserver.py %COMMANDLINE_ARGS%
pause
