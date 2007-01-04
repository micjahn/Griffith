@rem *** Used to create a Python exe  
 
@rem ***** get rid of all the old files in the build folder 
@rd /S /Q build 
@rd /S /Q dist 

@mkdir dist\etc
@mkdir dist\share
@mkdir dist\lib
@mkdir dist\share\locale

@rem ***** create the exe 

@python.exe -OO winsetup.py py2exe

@xcopy c:\gtk\etc c:\griffith\dist\etc /s /e
@xcopy c:\gtk\lib c:\griffith\dist\lib /s /e
@xcopy c:\gtk\share\locale c:\griffith\dist\share\locale /s /e

@copy c:\gtk\share\themes\MS-Windows\gtk-2.0\*.* c:\griffith\dist\
@copy c:\gtk\bin\jpeg62.dll c:\griffith\dist\
@rem **** pause so we can see the exit codes 