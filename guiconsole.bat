@echo off
set curpath=%~dp0

cd ..
set KBE_ROOT=E:/ComblockEngine/2/kbengine-2.5.11
set KBE_RES_PATH=%KBE_ROOT%/kbe/res/;%curpath%/;%curpath%/scripts/;%curpath%/res/
set KBE_BIN_PATH=%KBE_ROOT%/kbe/bin/server/

cd %KBE_ROOT%/kbe/tools/server/guiconsole/
start guiconsole.exe
