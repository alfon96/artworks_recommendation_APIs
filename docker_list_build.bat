@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

FOR %%f IN (Dockerfile*) DO (
    echo Building and running %%f
    SET "dockerfile_name=%%~nf"
    SET "dockerfile_port=!dockerfile_name:Dockerfile_=!"

    docker build -t docker_!dockerfile_port! -f %%f .
    
    start cmd /k "docker run --rm -it -p !dockerfile_port!:!dockerfile_port!/tcp docker_!dockerfile_port!"
)
