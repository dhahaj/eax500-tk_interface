
@ECHO Packaging executable...
@ECHO.

pyinstaller --onefile --noconsole --icon=icon.ico %1 --name=%2 --add-data=%3;.

@ECHO.
@ECHO Packaging complete!



