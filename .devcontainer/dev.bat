@echo off
REM Development container helper script for Windows
REM Works with cmd.exe and PowerShell

setlocal

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "COMPOSE_FILE=%SCRIPT_DIR%docker-compose.yml"
set "CONTAINER_NAME=asdana-devcontainer"

REM Detect docker compose command (with or without hyphen)
docker-compose version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "DOCKER_COMPOSE=docker-compose"
) else (
    docker compose version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "DOCKER_COMPOSE=docker compose"
    ) else (
        echo Error: Docker Compose is not installed.
        echo Please install Docker Desktop or Docker Compose.
        exit /b 1
    )
)

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="--help" goto help
if "%1"=="-h" goto help
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="shell" goto shell
if "%1"=="logs" goto logs
if "%1"=="rebuild" goto rebuild

echo Error: Unknown command '%1'
echo.
goto help

:help
echo Asdana Development Container Helper
echo.
echo Usage: dev.bat [command]
echo.
echo Commands:
echo   start       Build and start the development container
echo   stop        Stop the development container
echo   restart     Restart the development container
echo   shell       Open a shell in the running container
echo   logs        Show container logs
echo   rebuild     Rebuild the container from scratch
echo   help        Show this help message
echo.
echo Examples:
echo   dev.bat start    # Start the dev environment
echo   dev.bat shell    # Enter the container
echo   dev.bat logs     # View logs
goto end

:start
echo Starting development container...
cd /d "%PROJECT_ROOT%"
%DOCKER_COMPOSE% -f "%COMPOSE_FILE%" up -d
echo.
echo Development container started!
echo.
echo To access the container:
echo   dev.bat shell
echo.
echo Or use:
echo   docker exec -it %CONTAINER_NAME% bash
goto end

:stop
echo Stopping development container...
cd /d "%PROJECT_ROOT%"
%DOCKER_COMPOSE% -f "%COMPOSE_FILE%" down
echo Container stopped
goto end

:restart
call :stop
call :start
goto end

:shell
docker ps --filter "name=%CONTAINER_NAME%" --format "{{.Names}}" | findstr /C:"%CONTAINER_NAME%" >nul
if errorlevel 1 (
    echo Error: Container is not running. Start it first with:
    echo   dev.bat start
    exit /b 1
)
echo Opening shell in container...
docker exec -it %CONTAINER_NAME% bash
goto end

:logs
cd /d "%PROJECT_ROOT%"
%DOCKER_COMPOSE% -f "%COMPOSE_FILE%" logs -f
goto end

:rebuild
echo Rebuilding development container...
echo WARNING: This will remove all volumes and delete any data in the database!
set /p CONFIRM="Are you sure you want to continue? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo Rebuild cancelled.
    goto end
)
cd /d "%PROJECT_ROOT%"
%DOCKER_COMPOSE% -f "%COMPOSE_FILE%" down -v
%DOCKER_COMPOSE% -f "%COMPOSE_FILE%" build --no-cache
%DOCKER_COMPOSE% -f "%COMPOSE_FILE%" up -d
echo Container rebuilt and started
goto end

:end
endlocal
