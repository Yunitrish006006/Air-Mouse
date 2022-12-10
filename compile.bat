set file=%1%
echo compile:%file%
pyinstaller -F -w %file%