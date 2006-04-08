@rem *** Used to create a Python exe  
 
@rem ***** get rid of all the old files in the build folder 
@rd /S /Q build 
@rd /S /Q dist 
 
@rem ***** create the exe 
@python.exe -OO winsetup.py py2exe --bundle 1
@mkdir dist\etc

@xcopy c:\gtk\etc c:\griffith\dist\etc /s /e
@xcopy c:\gtk\lib c:\griffith\dist\lib /s /e
@copy c:\gtk\share\themes\MS-Windows\gtk-2.0\*.* c:\griffith\dist\
@copy c:\gtk\bin\jpeg62.dll c:\griffith\dist\
@rem **** pause so we can see the exit codes 