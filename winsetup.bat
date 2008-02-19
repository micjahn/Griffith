@echo off

rem *** Used to create a Python exe  

set GTKDIR=%GTK_BASEPATH%

set GRIFFITHDIR=.\

rem *** check the configuration
if not exist "%GTKDIR%" (
   echo Can't find directory %GTKDIR%.
   goto END
)

if not exist "%GRIFFITHDIR%" (
   echo Can't find directory %GRIFFITHDIR%.
   goto END
)

rem ***** get rid of all the old files in the build folder
if exist "%GRIFFITHDIR%\build" rd /S /Q build 
if exist "%GRIFFITHDIR%\dist" rd /S /Q dist 

mkdir dist\etc
mkdir dist\share
mkdir dist\lib
mkdir dist\share\locale

rem ***** create the exe 

python.exe -OO winsetup.py py2exe

if not "%ERRORLEVEL%" == "0" (
   pause
)

if not exist "dist\images\PluginMovieIMDB.png" (
   echo dist\images\PluginMovieIMDB.png not found.
   echo Extra-artwork missing ?
   pause
)

xcopy "%GTKDIR%\etc" "%GRIFFITHDIR%\dist\etc" /s /e
xcopy "%GTKDIR%\lib" "%GRIFFITHDIR%\dist\lib" /s /e
xcopy "%GTKDIR%\share\locale" "%GRIFFITHDIR%\dist\share\locale" /s /e

copy "%GTKDIR%\share\themes\MS-Windows\gtk-2.0\*.*" "%GRIFFITHDIR%\dist\"
copy "%GTKDIR%\bin\jpeg62.dll" "%GRIFFITHDIR%\dist\"

:END

rem **** pause so we can see the exit codes
pause
