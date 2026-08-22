@echo off
setlocal EnableExtensions

REM Rebuild Panchang API image and push to Docker Hub.
REM Usage:
REM   rebuild-and-push.bat
REM   rebuild-and-push.bat --no-cache

cd /d "%~dp0"

set "IMAGE=smohanty010620/panchang-api:latest"
set "NO_CACHE="

if /I "%~1"=="--no-cache" set "NO_CACHE=--no-cache"
if /I "%~1"=="/no-cache" set "NO_CACHE=--no-cache"

echo.
echo === Docker Hub login check ===
docker login
if errorlevel 1 (
  echo ERROR: docker login failed.
  exit /b 1
)

echo.
echo === Building %IMAGE% %NO_CACHE% ===
docker compose build %NO_CACHE% api
if errorlevel 1 (
  echo ERROR: docker compose build failed.
  exit /b 1
)

echo.
echo === Pushing %IMAGE% ===
docker push "%IMAGE%"
if errorlevel 1 (
  echo ERROR: docker push failed.
  exit /b 1
)

echo.
echo === Done ===
docker images "%IMAGE%" --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}"
echo.
echo Hub: https://hub.docker.com/r/smohanty010620/panchang-api
exit /b 0
