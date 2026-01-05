@echo off
echo [Project Aether Launcher]
echo Fixing environment variables...
SET PATH=C:\Program Files\nodejs;%PATH%
echo Environment repaired.
echo.
echo Starting Application...
echo Access URL: http://localhost:5173
echo.
npm run dev
pause
