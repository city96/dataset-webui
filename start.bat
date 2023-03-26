@echo off

REM Webserver arguments (see webserver.py --help)
set COMMANDLINE_ARGS=

REM Dependency downloader arguments (see download_dependencies.py --help)
set DEPENDENCY_ARGS=



if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
echo Downloading Dependencies
call python download_dependencies.py %DEPENDENCY_ARGS%
echo Starting webui
call python webserver.py %COMMANDLINE_ARGS%
pause
