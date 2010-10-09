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
mkdir dist\share\themes\MS-Windows\gtk-2.0

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
if not "%ERRORLEVEL%" == "0" (pause)
xcopy "%GTKDIR%\lib" "%GRIFFITHDIR%\dist\lib" /s /e
if not "%ERRORLEVEL%" == "0" (pause)
xcopy "%GTKDIR%\share\locale" "%GRIFFITHDIR%\dist\share\locale" /s /e
if not "%ERRORLEVEL%" == "0" (pause)

xcopy "%GTKDIR%\share\themes\MS-Windows\gtk-2.0\*.*" "%GRIFFITHDIR%\dist\" /s /e
if not "%ERRORLEVEL%" == "0" (pause)
xcopy "%GTKDIR%\bin\jpeg62.dll"   "%GRIFFITHDIR%\dist\" /s /e
if not "%ERRORLEVEL%" == "0" (pause)

copy "%GRIFFITHDIR%\AUTHORS"     "%GRIFFITHDIR%\dist\"
copy "%GRIFFITHDIR%\COPYING"     "%GRIFFITHDIR%\dist\"
copy "%GRIFFITHDIR%\INSTALL"     "%GRIFFITHDIR%\dist\"
copy "%GRIFFITHDIR%\NEWS"        "%GRIFFITHDIR%\dist\"
copy "%GRIFFITHDIR%\README"      "%GRIFFITHDIR%\dist\"
copy "%GRIFFITHDIR%\THANKS"      "%GRIFFITHDIR%\dist\"
copy "%GRIFFITHDIR%\TRANSLATORS" "%GRIFFITHDIR%\dist\"

rem *** remove unnecessary files
del /S /F /Q "%GRIFFITHDIR%\dist\*.pyo"
del /S /F /Q "%GRIFFITHDIR%\dist\*.a"
del /S /F /Q "%GRIFFITHDIR%\dist\*.lib"
del /S /F /Q "%GRIFFITHDIR%\dist\xml2Conf.sh"
del /S /F /Q "%GRIFFITHDIR%\dist\*.pyc"
del /S /F /Q "%GRIFFITHDIR%\dist\*.la"
del /S /F /Q "%GRIFFITHDIR%\dist\*.def"
rd /S /Q "%GRIFFITHDIR%\dist\lib\pkgconfig"
rd /S /Q "%GRIFFITHDIR%\dist\lib\gtkglext-1.0"
rd /S /Q "%GRIFFITHDIR%\dist\lib\gtk-2.0\include"
rd /S /Q "%GRIFFITHDIR%\dist\lib\glib-2.0"

:END

rem **** pause so we can see the exit codes
pause
