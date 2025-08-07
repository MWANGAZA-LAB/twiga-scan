@echo off
REM 🚀 Twiga Scan Quick Deployment Script (Windows)
REM This script automates the deployment process for different environments

setlocal enabledelayedexpansion

REM Set colors for output
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Function to print colored output
:print_status
echo %BLUE%[INFO]%NC% %~1
goto :eof

:print_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM Function to check if command exists
:command_exists
where %~1 >nul 2>&1
if %errorlevel% equ 0 (
    set "exists=1"
) else (
    set "exists=0"
)
goto :eof

REM Function to check prerequisites
:check_prerequisites
call :print_status "Checking prerequisites..."

set "missing_deps="

call :command_exists docker
if "!exists!"=="0" set "missing_deps=!missing_deps! docker"

call :command_exists docker-compose
if "!exists!"=="0" set "missing_deps=!missing_deps! docker-compose"

call :command_exists git
if "!exists!"=="0" set "missing_deps=!missing_deps! git"

if not "!missing_deps!"=="" (
    call :print_error "Missing required dependencies:!missing_deps!"
    call :print_status "Please install the missing dependencies and try again."
    exit /b 1
)

call :print_success "All prerequisites are installed"
goto :eof

REM Function to setup environment
:setup_environment
call :print_status "Setting up environment..."

if not exist .env (
    call :print_status "Creating .env file from template..."
    copy env.example .env >nul
    call :print_warning "Please edit .env file with your configuration before continuing"
)

if not exist logs mkdir logs

call :print_success "Environment setup completed"
goto :eof

REM Function to build and start services
:start_services
set "environment=%~1"
if "!environment!"=="" set "environment=development"

call :print_status "Starting services in !environment! mode..."

if "!environment!"=="production" (
    docker-compose -f docker-compose.prod.yml up -d --build
) else (
    docker-compose up -d --build
)

if %errorlevel% neq 0 (
    call :print_error "Failed to start services"
    exit /b 1
)

call :print_success "Services started successfully"
goto :eof

REM Function to check service health
:check_health
call :print_status "Checking service health..."

REM Wait for services to be ready
timeout /t 10 /nobreak >nul

REM Check backend health
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Backend is healthy"
) else (
    call :print_error "Backend health check failed"
    exit /b 1
)

REM Check frontend (basic connectivity)
curl -f http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Frontend is accessible"
) else (
    call :print_warning "Frontend health check failed (may still be starting)"
)

REM Check database
docker-compose exec -T postgres pg_isready -U postgres >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Database is healthy"
) else (
    call :print_error "Database health check failed"
    exit /b 1
)
goto :eof

REM Function to show service status
:show_status
call :print_status "Service Status:"
echo ==================

REM Docker services
docker-compose ps

echo.
call :print_status "Service URLs:"
echo ==============
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
goto :eof

REM Function to stop services
:stop_services
call :print_status "Stopping services..."
docker-compose down
call :print_success "Services stopped"
goto :eof

REM Function to view logs
:view_logs
set "service=%~1"

if "!service!"=="" (
    call :print_status "Showing all logs (Ctrl+C to exit)..."
    docker-compose logs -f
) else (
    call :print_status "Showing !service! logs (Ctrl+C to exit)..."
    docker-compose logs -f "!service!"
)
goto :eof

REM Function to restart services
:restart_services
call :print_status "Restarting services..."
docker-compose restart
call :print_success "Services restarted"
goto :eof

REM Function to clean up
:cleanup
call :print_status "Cleaning up..."
docker-compose down -v --remove-orphans
docker system prune -f
call :print_success "Cleanup completed"
goto :eof

REM Function to show help
:show_help
echo 🚀 Twiga Scan Quick Deployment Script
echo =====================================
echo.
echo Usage: %~nx0 [COMMAND] [OPTIONS]
echo.
echo Commands:
echo   start [env]     Start services (development^|production^)
echo   stop            Stop all services
echo   restart         Restart all services
echo   status          Show service status and URLs
echo   logs [service]  View logs (all services or specific service^)
echo   health          Check service health
echo   setup           Setup environment (create .env, etc.^)
echo   cleanup         Stop services and clean up Docker resources
echo   help            Show this help message
echo.
echo Examples:
echo   %~nx0 start              # Start in development mode
echo   %~nx0 start production   # Start in production mode
echo   %~nx0 logs backend       # View backend logs
echo   %~nx0 status             # Show service status
echo.
goto :eof

REM Main script logic
set "command=%~1"
if "!command!"=="" set "command=help"
set "option=%~2"

if "!command!"=="start" (
    call :check_prerequisites
    call :setup_environment
    call :start_services "!option!"
    call :check_health
    call :show_status
) else if "!command!"=="stop" (
    call :stop_services
) else if "!command!"=="restart" (
    call :restart_services
    call :check_health
    call :show_status
) else if "!command!"=="status" (
    call :show_status
) else if "!command!"=="logs" (
    call :view_logs "!option!"
) else if "!command!"=="health" (
    call :check_health
) else if "!command!"=="setup" (
    call :check_prerequisites
    call :setup_environment
) else if "!command!"=="cleanup" (
    call :cleanup
) else if "!command!"=="help" (
    call :show_help
) else (
    call :print_error "Unknown command: !command!"
    echo.
    call :show_help
    exit /b 1
)

endlocal
