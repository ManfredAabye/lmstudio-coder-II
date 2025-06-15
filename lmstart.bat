@echo off
chcp 65001 >nul
setlocal

:: Verzeichnis __pycache__ löschen
if exist __pycache__ (
    echo Lösche Verzeichnis __pycache__...
    rmdir /s /q __pycache__
) else (
    echo Verzeichnis __pycache__ nicht gefunden.
)

if "%1"=="build" (
    echo Erstelle EXE...
    pyinstaller --onefile lmstudioplug.py
) else (
    echo Starte LMStudio Plugin...
    python lmstudioplug.py
)

if "%1"=="xbuild" (
    echo Building executable...
    pyinstaller --onefile --windowed --name lmstudioplug lmstudioplug.py
    echo Build complete. Check dist folder.
)

if "%1"=="clean" (
    echo Bereinige Build-Ordner...
    rmdir /s /q build
    rmdir /s /q dist
    del lmstudioplug.spec
)

endlocal
pause