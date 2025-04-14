@echo off
SET SCRIPT_NAME=tidytv.py
SET DIST_FOLDER=dist
SET BUILD_FOLDER=build

echo Building %SCRIPT_NAME% into EXE...

REM Optional: Clean previous builds
IF EXIST %DIST_FOLDER% rmdir /s /q %DIST_FOLDER%
IF EXIST %BUILD_FOLDER% rmdir /s /q %BUILD_FOLDER%
IF EXIST %SCRIPT_NAME:.py=.spec% del %SCRIPT_NAME:.py=.spec%

echo.
echo ✅ Activating virtual environment...
call venv\\Scripts\\activate

REM Build the executable
pyinstaller --noconsole --onefile %SCRIPT_NAME%

echo.
echo Done! Your EXE is in the %DIST_FOLDER% folder.
pause
