@echo off

REM Webserver arguments (see webserver.py --help)
REM --autolaunch   [Open webui in default browser]
REM --port 8080    [Port to host webui on]
REM --listen       [Allow access from LAN (NOT RECOMMENDED)]
set COMMANDLINE_ARGS=

REM Dependency downloader arguments (see download_dependencies.py --help)
REM --no-auto          [Manually ask about each download]
REM --no-verify        [Do not verify file contents]
REM --overwrite        [Overwrite/re-download files on disk]
REM --skip-cropperjs   [Don't download Cropper.js]
REM --skip-tags        [Don't download/check tags]
REM --tag-catbox       [Use catbox.moe instead of gist]
REM --force-tag-scrape [Start tag scraper]
set DEPENDENCY_ARGS=

if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
echo Downloading Dependencies
call python download_dependencies.py %DEPENDENCY_ARGS%
echo Starting webui
call python webserver.py %COMMANDLINE_ARGS%
pause
